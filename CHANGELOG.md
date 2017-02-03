## 0.5.2
"Tiny"' fix

## 0.5.1
Now functions can be asynchronous.
```python
async def post(req, api):
    return await my_async_function()
```

# )0.5
Added json translation

Now received
```json
{
    "var1[0]": "value0", 
    "var1[1]": "value1",
    "var2[key1]": "value2",
    "var2[key2]": "value3"
}
```
will be
```json
{
    "var1": [
        "value0", 
        "value1"
    ],
    "var2": {
        "key1": "value2",
        "key2": "value3"
    }
}
```

## 0.4.2
Tiny fixes

## 0.4.1
Fixed cors

# v0.4
Added versioning system (now `--version` is possible)

## v0.3.2
Little fix on logs

## v0.3.1
Fixed vars variable

# v0.3
Added `--config` to command line to select config

Added `log` options to config, now it's possible to log to a file

## v0.2.3
Changed `req.param` to `req.params`

## v0.2.2
Now it is possible to have multiple endpoints (it was impossible before? Yes...)
Also possible to have no utils

## v0.2.1
Fixed inexistent cors

# v0.2
Added cors support

## v0.1.6
Fixed readme (did I really need 6 patches? w/e)

# v0.1
Created project