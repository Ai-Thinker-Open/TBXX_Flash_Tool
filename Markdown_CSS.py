html_head = """
<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
<style> 
    body {
        font-family: Helvetica, arial, sans-serif;
        font-size: 14px;
        line-height: 1.6;
        padding-top: 10px;
        padding-bottom: 10px;
        padding: 30px; }
        
    h1, h2, h3, h4, h5, h6 {
        margin: 20px 0 10px;
        padding: 0;
        font-weight: bold;
        -webkit-font-smoothing: antialiased;
        cursor: text;
        position: relative; }

    h1 tt, h1 code {
        font-size: inherit; }
    
    h2 tt, h2 code {
        font-size: inherit; }
    
    h3 tt, h3 code {
        font-size: inherit; }
    
    h4 tt, h4 code {
        font-size: inherit; }
    
    h5 tt, h5 code {
        font-size: inherit; }
    
    h6 tt, h6 code {
        font-size: inherit; }
    
    h1 {
        font-size: 28px;
        color: black; }
    
    h2 {
        font-size: 24px;
        border-bottom: 1px solid #cccccc;
        color: black; }
    
    h3 {
        font-size: 18px; }
    
    h4 {
        font-size: 16px; }
    
    h5 {
        font-size: 14px; }
table,table tr th, table tr td { border:1px solid #000000; empty-cells:show;}
table { width: 200px; min-height: 25px; line-height: 25px; border-collapse: collapse;empty-cells:show;} 
</style>
</head>
<body>
"""

html_tail = """
</body>
</html>
"""

html_test = """
<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type" />
<style type="text/css">
table,table tr th, table tr td { border:1px solid #0094ff; }
table { width: 200px; min-height: 25px; line-height: 25px; text-align: center; border-collapse: collapse;}   
h4 {color:red;}
</style>
</head>
<body>

<h4>这个表格有一个标题，以及粗边框：</h4>

<table>
<tr>
  <td>100</td>
  <td>200</td>
  <td>300</td>
</tr>
<tr>
  <td>400</td>
  <td>500</td>
  <td>600</td>
</tr>
</table>

</body>

</html>
"""