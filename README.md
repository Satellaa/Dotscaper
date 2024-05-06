<h1 align="center">Dotscaper</h1>
<p align="center">
  <img src="/public/dotscaper.png" width="200" height="184"/>
</p>

A tool to scrape _Yu-Gi-Oh!_ Official Card Game card information and prices from [YAML Yugi](https://github.com/DawnbrandBots/yaml-yugi), [Yugipedia](https://yugipedia.com/wiki/Yugipedia), [TCG Corner](https://tcg-corner.com/), [Bigweb](https://www.bigweb.co.jp/ja/products/yugioh), etc. and store them in [MongoDB](https://www.mongodb.com).

## Installing

> First, you should create a virtual environment to avoid any conflicts with existing packages.
```
$ git clone https://github.com/Satellaa/Dotscaper.git
$ cd Dotscaper
$ pip install -r requirements.txt
```

## Setup

See [.env](.env)

## Usage

You can run `python main.py` with the following arguments:
| Name  | Description | Condition |
| ------------- | ------------- | ------------- |
| `--init`  | Scrape card information and prices, then store it in MongoDB.  | Must be used first.              |
| `--update-card-info`  | Scrape card information, then store it in MongoDB.  | Should only be used after using `--init`.               |
| `--update-card-prices`  | Scrape card prices, then store it in MongoDB.  | Should only be used after using `--init`.               |

## Contributing

Please use [pre-commit](https://pre-commit.com/).