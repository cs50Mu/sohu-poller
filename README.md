## sohu poller
check the availability of all the pages of a website recursively

### How to use
    # clone the code from github
    git clone https://github.com/cs50Mu/sohu-poller.git
    
    # install the requirements
    cd sohu-poller
    pip install -r requirements.txt
    
    # run it
    python poller.py
### Configuration
##### conf/poller.cfg
- `thread_num`   
the number of threads
- `base_url`     
the url of the website that you want to check
- `timeout`      
request timeout
