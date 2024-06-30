def table(field: list, cell: list, params: dict={}):
    rtn = "<table"
    for key in params:
        rtn+=f" {key}=\"{params[key]}\""
    rtn+=">"
    rtn+="<thead>"
    rtn+="<tr>"
    for i in field:
        rtn+=f"<th>{i}</th>"
    rtn+="</tr>"
    rtn+="</thead>"
    rtn+="<tbody>"
    for i in cell:
        rtn+="<tr>"
        for j in i:
            rtn+=f"<td>{j}</td>"
        rtn+="</tr>"
    rtn+="</tbody>"
    rtn+="</table>"
    return rtn

def hyperlink(text: str, link: str, params: dict={}):
    rtn = f"<a href=\"{link}\""
    for key in params:
        rtn += f" {key}=\"{params[key]}\""
    rtn+= ">"
    rtn+= text
    rtn+= "</a>"
    return rtn

def linebreak():
    return "<br>"

def div(text: str, params: dict={}):
    rtn = f"<div"
    for key in params:
        rtn += f" {key}=\"{params[key]}\""
    rtn+= ">"
    rtn+= text
    rtn+= "</div>"
    return rtn

def input(params: dict={}):
    rtn = f"<input"
    for key in params:
        rtn += f" {key}=\"{params[key]}\""
    rtn += ">"
    return rtn
    