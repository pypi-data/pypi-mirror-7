# lolapi

A simple Python wrapper for the League of Legends API by Riot Games at [https://developer.riotgames.com/api/methods](https://developer.riotgames.com/api/methods).

### Usage

```python
import lolapi

api = lolapi.LolApi(region='na', key='<your_api_key>')

summoners = api.summoners.get_all()
items = api.data.get_items()
...
...
```
