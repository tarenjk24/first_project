const bar = document.getElementById('bar');
const close = document.getElementById('close') 
const nav = document.getElementById('navbar') 

if(bar){
    bar.addEventListener('click', () =>{
        nav.classListadd('active');
    })
}

if(close){
    clsoe.addEventListener('click', () =>{
        nav.classList.remove('active');
    })
}