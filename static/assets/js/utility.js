
function GetParamString(name) {
    // 读取url参数
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

var zeroize = function (value, length) {
    if (!length) length = 2;
    value = String(value);
    for (var i = 0, zeros = ''; i < (length - value.length); i++) {
        zeros += '0';
    }
    return zeros + value;
}

function GetDateStr(DelDayCount) {
    // 读取DelDayCount天前的日期
    var dd = new Date();
    dd.setDate(dd.getDate() - DelDayCount);//获取AddDayCount天后的日期
    var y = dd.getFullYear();
    var m = zeroize(dd.getMonth() + 1);//获取当前月份的日期
    var d = zeroize(dd.getDate());
    return y + "-" + m + "-" + d + " 00:00:00";
}

function getSelectedOptions(sel) {
    // select标签多选
    var opts = [], opt;
    // loop through options in select list
    for (var i = 0, len = sel.options.length; i < len; i++) {
        opt = sel.options[i];

        // check if selected
        if (opt.selected) {
            // add to array of option elements to return from this function
            opts.push(opt.value);
        }
    }
    return opts
}

function CheckInputIntFloat(oInput) {
    if ('' != oInput.value.replace(/\d{1,}\.{0,1}\d{0,}/, '')) {
        oInput.value = oInput.value.match(/\d{1,}\.{0,1}\d{0,}/) == null ? '' : oInput.value.match(/\d{1,}\.{0,1}\d{0,}/);
    }
}


// ajax 对象
function ajaxObject() {
    var xmlHttp;
    try {
        // Firefox, Opera 8.0+, Safari
        xmlHttp = new XMLHttpRequest();
        }
    catch (e) {
        // Internet Explorer
        try {
                xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
            } catch (e) {
            try {
                xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) {
                alert("您的浏览器不支持AJAX！");
                return false;
            }
        }
    }
    return xmlHttp;
}

// ajax post请求：
function ajaxPost ( url , data , fnSucceed , fnFail , fnLoading ) {
    var ajax = ajaxObject();
    ajax.open( "post" , url , true );
    ajax.setRequestHeader( "Content-Type" , "application/x-www-form-urlencoded" );
    ajax.onreadystatechange = function () {
        if( ajax.readyState == 4 ) {
            if( ajax.status == 200 ) {
                fnSucceed( ajax.responseText );
            }
            else {
                fnFail( "HTTP请求错误！错误码："+ajax.status );
            }
        }
        else {
            fnLoading();
        }
    };
    ajax.send( data );

}