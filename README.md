# Sayari_Challenge_Solution

Solution for https://gist.github.com/jvani/57200744e1567f33041130840326d488
## Local Run

```bash
#source yourvenv/bin/activate
pip install -r requirements.txt
```

```bash
#specify your Search Letter and graph output file
scrapy crawl cp_search_spider -a startswith='X' -a graph_output='graph_X.png' -O items.json --logfile output.log
```
<br>

## Docker Run

```bash
docker build -t myspider .
```

```bash
docker run myspider
```

## Info about crawler
Crawler outputs data in json format in `items.json`, all the data it can find, and then later some features are extracted to draw our graph.  
Crawler outputs two spring_layout graphs with and without label.
<br>
<br>
[Example Graph Generated with labels](https://github.com/mnabil/sayari_challenge_solution/blob/main/graph_X.png)
<br>
[Example Graph Generated without labels](https://github.com/mnabil/sayari_challenge_solution/blob/main/nolabel_graph_X.png)
<br>
<br>
COLOR_SCHEME:<br>
&emsp;Company':  light Blue <br>
&emsp;OWNER' : Green <br>
&emsp;COMM_REG_AGENT : Orange<br>
&emsp;REG_AGENT': Pink <br>
