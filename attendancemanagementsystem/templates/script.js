

document.getElementById('menuIcon').addEventListener('click', function() {
    document.getElementById('menu').style.left = '0';
    document.getElementById('overlay').style.display = 'block';
});

document.getElementById('closeBtn').addEventListener('click', function() {
    document.getElementById('menu').style.left = '-50%';
    document.getElementById('overlay').style.display = 'none';
});

document.getElementById('overlay').addEventListener('click', function() {
    document.getElementById('menu').style.left = '-50%';
    document.getElementById('overlay').style.display = 'none';
});

document.querySelectorAll('.menu ul li').forEach(function(item) {
    item.addEventListener('click', function() {
        document.querySelectorAll('.menu ul li').forEach(function(li) {
            li.classList.remove('selected');
        });
        item.classList.add('selected');
    });
});



















document.addEventListener("DOMContentLoaded", function() {
    const easyTouch = document.getElementById("easyTouch");
    let isDragging = false;

    easyTouch.addEventListener("mousedown", function(e) {
        e.preventDefault();
        let shiftX = e.clientX - easyTouch.getBoundingClientRect().left;
        let shiftY = e.clientY - easyTouch.getBoundingClientRect().top;

        function moveAt(pageX, pageY) {
            easyTouch.style.left = pageX - shiftX + "px";
            easyTouch.style.top = pageY - shiftY + "px";
        }

        function onMouseMove(event) {
            isDragging = true;
            moveAt(event.pageX, event.pageY);
        }

        document.addEventListener("mousemove", onMouseMove);

        easyTouch.addEventListener("mouseup", function() {
            document.removeEventListener("mousemove", onMouseMove);
            setTimeout(() => { isDragging = false; }, 0); // Delay to differentiate click and drag
        });

        easyTouch.addEventListener("dragstart", function() {
            return false;
        });
    });

    easyTouch.addEventListener("click", function() {
        if (!isDragging) {
            window.location.href = "nexisphereai/nexisphereai.html";
        }
    });
});