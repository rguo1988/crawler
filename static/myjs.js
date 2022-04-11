function showLoading (event) {
    let oevent = event || window.event
    if (document.all) {
        oevent.cancelBubble = true
    } else {
        oevent.stopPropagation()
    }
    if (document.getElementById('loading').style.display === 'none' || document.getElementById('loading').style.display === '') {
        document.getElementById('loading').style.display = 'block'
    }
}
