function toggle(source, name) {
  checkboxes = document.getElementsByName(name);
  for(var i in checkboxes)
    checkboxes[i].checked = source.checked;
}