## Setup


#### 1. Install all the dependencies
```
pip install -r requirements.txt
```

#### 2. Run the Main service

```
python3 main.py
```

#### 3. Run the dummy POST endpoint which recieves the PDF and download it to the root folder
- You can skip this step of running the dummy POST endpoint and replace http://localhost:9000/accept-pdf with the actual Insights Endpoint.
```
python3 post.py
```

#### 4. Visit http://localhost/docs and make a request to /fetch-data with suitable request body
```
{
  "categories": [
    ""
  ],
  "start_date": "",
  "end_date": ""
}
```
