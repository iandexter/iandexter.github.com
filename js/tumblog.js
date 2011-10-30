function displayTumblog(data){var count=data.count;var yesterday=0;for(var i=0;i<count;i++){var today=new Date(parseInt(data.value.items[i]['y:published'].utime)*1000);if(yesterday!=today.getDate()){yesterday=today.getDate();displayTitle(today);}
displayTumblogItem(data.value.items[i]);}
jsonPipe.removeScript();}
function displayTitle(date){var title=document.createElement('h2');title.className="tumblogItemTitle";title.innerHTML=niceDate(date);document.getElementById('content').appendChild(title);}
function displayTumblogItem(item){var wrapper=document.createElement('div');wrapper.className="tumblogItem";wrapper.id=item['y:published'].utime;var timestamp=document.createElement('span');timestamp.className="timestamp";var date=new Date(parseInt(item['y:published'].utime)*1000);timestamp.innerHTML=date.getHours().pad(2)+":"+date.getMinutes().pad(2);var link=document.createElement('a');link.href=item.link;link.target="_none";link.className=item['source'];link.innerHTML=item.title;wrapper.appendChild(timestamp);wrapper.appendChild(link);document.getElementById('content').appendChild(wrapper);}
function getTumblogItems(items){var pipeRequest='http://pipes.yahoo.com/pipes/pipe.run?_id=qhEAr2LW3BGeFuGa8TxBKg&_render=json&_callback=displayTumblog&items='+items;jsonPipe=new jsonScriptRequest(pipeRequest);jsonPipe.buildScript();}
function jsonScriptRequest(jsonURL){this.url=jsonURL;var cacheToken=hex_md5((new Date()).getTime()+'');this.headElt=document.getElementsByTagName('head')[0];this.scriptID=cacheToken;this.noCache='&cache='+cacheToken;}
jsonScriptRequest.prototype.buildScript=function(){this.jsonScript=document.createElement('script');this.jsonScript.type="text/javascript";this.jsonScript.id=this.scriptID;this.jsonScript.src=this.url+this.noCache;this.headElt.appendChild(this.jsonScript);}
jsonScriptRequest.prototype.removeScript=function(){this.headElt.removeChild(this.jsonScript);}
function removeChildren(){var content=document.getElementById('content');while(content.firstChild)content.removeChild(content.firstChild);}
function niceDate(date){var months=new Array("January","February","March","April","May","June","July","August","September","October","November","December");var niceDate=date.getDate().pad(2)+" "+months[date.getMonth()]+" "+date.getFullYear();return niceDate;}
Number.prototype.pad=function(length){var str=''+this;while(str.length<length)str='0'+str;return str;}