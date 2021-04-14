// Java Script implemented in base.html
// implemented in the last lines of base.html

/*
-------------------------------------------------------------------------------------------------
    calling of necessary function after DOM Content is loaded
-------------------------------------------------------------------------------------------------
*/
document.addEventListener("DOMContentLoaded", function(){
    addTitleAttrToAs();
})

// add to all links the title property in order to prevent repositioning on making the fond bold on hovering
function addTitleAttrToAs(){
    var As = document.getElementsByTagName("a");
    for(i=0; i < As.length; i++)
        As[i].setAttribute("title", As[i].innerText);
}

/*
-------------------------------------------------------------------------------------------------
    main navigation scripts
-------------------------------------------------------------------------------------------------
*/

function toggleDropDown(id){
    /*
        <div id="[id]">
            <a class="toggle [active]"></a>
            <div class="drop-down [active]"></div>
        </div>

        toggles appearance of class active
            -> css handles appearance, etc.
    */
    try {
        ele = document.getElementById(id);
        ele.getElementsByClassName("toggle")[0].classList.toggle("active");
        ele.getElementsByClassName("drop-down")[0].classList.toggle("active");
    } catch(e) {
        console.error('function toggleDropDown called with invalid id or the id of an element whose HTML-Tree is not build correctly.');
        console.error(e);
    }
}