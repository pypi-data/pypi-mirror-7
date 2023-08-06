/* Simple image viewer for eClaircie, by Jean-Baptiste "Jiba" Lamy.
   Licence : GNU GPL v3 */

function create_imageviewer() {
  document.write('\
<div id="imageviewer" style="position:fixed;width:100%;height:100%;left:0px;top:0px;background-color:rgba(0,0,0,0.65);display:none;text-align:center;">\
<table onclick="hide_imageviewer();" style="width:100%;height:100%;"><tr>\
<td onclick="on_imageviewer_previous(event);" style="width:1em;font-size:400%;font-weight:bold;color:white;vertical-align:middle;cursor:pointer;"> &lt; </td>\
<td><img id="imageviewer-img" style="box-shadow: 0 0 30px 5px black;"/></td>\
<td onclick="on_imageviewer_next(event);" style="width:1em;font-size:400%;font-weight:bold;color:white;vertical-align:middle;cursor:pointer;"> &gt; </td>\
</tr></table></div>');
}

function hide_imageviewer() {
  document.getElementById("imageviewer").style.display = 'none';
  document.onkeydown = null;
}

function show_imageviewer(images, index) {
  imageviewer_images = images;
  document.getElementById("imageviewer").style.display = 'block';
  imageviewer_set_image(index);
  document.onkeydown = function(e) {
    e = e || window.event;
    switch (e.keyCode) {
      case 27:
        hide_imageviewer(); break;
      case 37:
        on_imageviewer_previous(e); break;
      case 39:
        on_imageviewer_next(e); break;
    }
  };
}

function on_imageviewer_next(e) {
  if(imageviewer_index == imageviewer_images.length - 1) hide_imageviewer();
  else imageviewer_set_image(imageviewer_index + 1);
  e.stopPropagation();
}

function on_imageviewer_previous(e) {
  if(imageviewer_index == 0) hide_imageviewer();
  else imageviewer_set_image(imageviewer_index - 1);
  e.stopPropagation();
}

function imageviewer_set_image(index) {
  imageviewer_index = index;
  var i = document.getElementById("imageviewer-img");
  i.src = imageviewer_images[imageviewer_index];
  i.style.maxWidth = window.innerWidth - 150 + "px";
  i.style.maxHeight = window.innerHeight - 10 + "px";
}
