/*参考：http://www.html5tricks.com/demo/jquery-pop-login-form/index.html#
* */

function init_login() {
    // 初始化登录模块
    $('#LoginBox').load('/template/account/login.html', function () {
    });
}

function pop_login_box () {
    //弹出登录窗口
    $("#login").hover(function () {
        $(this).stop().animate({
            opacity: '1'
        }, 600);
    }, function () {
        $(this).stop().animate({
            opacity: '0.6'
        }, 1000);
    });
    console.log("弹出登录窗口");
    $("#LoginBox").fadeIn("slow");

    //关闭登录窗口
    close_login_box();
    //登录提交(登录按钮触发)
    $("#loginSubmit").on('click', login_submit);
    //登录提交(回车触发)
    $(document).keyup(function (event) {
        if ($("#LoginBox").css('display') != 'none' && event.keyCode == 13) {
            login_submit();
        }
    });
}

function close_login_box() {
    //关闭登录窗口
    $("#closeBtn").hover(function () {
        $(this).css({color: 'black'})
    }, function () {
        $(this).css({color: '#999'})
    }).on('click', function () {
        console.log("关闭登录窗口");
        $("#LoginBox").fadeOut("fast");
        $("#login").stop().animate({
            opacity: '1'
        }, 1000);
    });
}

function logout() {
    //注销
    $.post('/logout', {}, function (data, status) {
        if (data["err_code"] == 0) {
            window.location.reload();
            alert("注销成功！");
        }
        else alert("注销失败：" + data["err_msg"]);
    })
}

function login_submit () {
    var account = $("#userName").val();
    var password = $("#passWord").val();
    var js_param = JSON.stringify({
        "account": account,
        "password": password
    });
    $.post("/login", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("登录成功！");
            window.location.reload();
            $("#LoginBox").fadeOut("fast");
            $("#login").stop().animate({
                opacity: '1'
            }, 1000);
        }
        else alert("登录失败：" + data["err_msg"]);
    })
}

function check_current_user(funLogin, funLogout){
    // 检查是否登录状态中
    var url_get_user = window.location.origin + "/get_user";
    $.post(url_get_user, {}, function (data, status) {
        if (data["err_code"] == 0) {
            $("#btnGroupDrop1").text("yzy");
            if(funLogin) {
                funLogin();
            }
        }
        else {
            $("#btnGroupDrop1").text("未登录");
            if(funLogout) {
                funLogout();
            }
        }
    })
}