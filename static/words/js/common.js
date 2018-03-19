function init_headers(sub_title) {
    // 根据选择初始化菜单导航栏
    $('.configHead').load('/template/words/headers.html', function (callback) {
        $("a[name='navbar']").each(function () {
            if ($(this).text() === sub_title) {
                $(this).attr('class', 'nav-link custom-active')
            }
        });
    });
}
