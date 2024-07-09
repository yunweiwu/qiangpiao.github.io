from selenium import webdriver
from selenium.webdriver.chrome.options import Options



if __name__ == '__main__':
    # 设置selenium使用chrome的无头模式
    chrome_options = Options()
    # 在启动浏览器时加入配置
    browser = webdriver.Chrome(options=chrome_options)
    # 打开百度
    browser.get('https://www.baidu.com/')
    # 等待加载，最多等待20秒
    browser.implicitly_wait(200)