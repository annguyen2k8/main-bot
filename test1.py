from html2image import Html2Image
hti = Html2Image()
hti = Html2Image(size=(500, 200))
html = """<h1> An interesting title </h1> This page will be red"""
css = "body {background: red;}"

hti.screenshot(html_str=html, css_str=css, save_as='red_page.png')