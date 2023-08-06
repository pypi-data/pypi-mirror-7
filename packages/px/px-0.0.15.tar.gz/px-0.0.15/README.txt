6px-python-sdk
==============

Simple usage:

```python
from _6px import PX

px = PX.init(
	user_id='YOUR USER ID',
	api_key='YOUR API KEY',
	api_secret='YOUR API SECRET'
)

px.load('img', '/path/to/picture.jpg')

out = px.output({ 'img': False })
out.resize({ 'width': 200, 'height': 400 })

px.save()
```
