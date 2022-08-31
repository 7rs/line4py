# line4py

## Installtion from [PyPI](https://pypi.org/project/line4py)

`pip install line4py`

## Installtion from [GitHub](https://github.com/7rs/line4py)

`pip install git+ssh://git@github.com/7rs/line4py.git@master`

## Usage

```python
from line4py import Client, ApplicationType

client = Client(ApplicationType.ANDROIDLITE, concurrency=30, secondary=True)
client.login_with_qrcode()
```
