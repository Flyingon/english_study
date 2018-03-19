
var origin_url = window.location.origin; // 不带路径的url地址
var var_word_type = "all";  // 记录此时的单词词性
var default_word_container_html = ""; // 添加编辑单词html,默认三行单词编辑框，用于刷新恢复


function active_nav_item(word_type) {
    // 词性导航栏选择
    $('#word-type-nav').find('li').each(function () {
        var link_btn = $(this).find('a');
        var class_attr = link_btn.attr('class');
        if (link_btn.attr('id') == word_type) {
            if (class_attr.indexOf("active") < 0) class_attr += " active";
        }
        else {
            class_attr = class_attr.replace(" active", "");
        }
        link_btn.attr('class', class_attr);
    });
}

function show_words_table(word_type) {
    // 根据词性选择并展示单词列表
    var_word_type = word_type;
    active_nav_item(word_type);
    var url = origin_url + "/words/synonym/" + word_type;
    $.get(url, function(data, status){
        var th_list = data["th_list"];
        var data = data["data"];
        make_table(th_list, data)
    });
    default_word_container_html = $("#container_add_word").html();
}

function make_table(th_list, data) {
    // 根据表头和数据生成表格
   $("#words_table").remove();
    // var wrap = $("<div id='wrap_request_statistic' class='col-md-6 col-md-offset-3'></div>");
    // wrap.css({
    //     position: "relative",
    //     top: "85px"
    // });

    var tab = $("<table id='words_table' class='table table-hover text-center mx-5' data-search=true data-search-on-enter-key=true strictSearch=true></table>");
    // var tab_search = '<div class="fixed-table-toolbar"><div class="columns columns-right btn-group pull-right"><button class="btn btn-default" type="button" name="toggle" aria-label="toggle" title="Toggle"><i class="glyphicon glyphicon-list-alt icon-list-alt"></i></button><div class="keep-open btn-group" title="Columns"><button type="button" aria-label="columns" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false"><i class="glyphicon glyphicon-th icon-th"></i> <span class="caret"></span></button><ul class="dropdown-menu" role="menu"><li role="menuitem"><label><input type="checkbox" data-field="0" value="0" checked="checked"> 名称</label></li><li role="menuitem"><label><input type="checkbox" data-field="1" value="1" checked="checked"> 标签</label></li><li role="menuitem"><label><input type="checkbox" data-field="2" value="2" checked="checked"> 类型</label></li><li role="menuitem"><label><input type="checkbox" data-field="3" value="3" checked="checked"> 默认</label></li><li role="menuitem"><label><input type="checkbox" data-field="4" value="4" checked="checked"> 描述</label></li></ul></div></div><div class="pull-right search"><input class="form-control" type="text" placeholder="Search"></div></div>'
    // tab.append($(tab_search));

    var head = "<thead>";
    for (var i in th_list) {
        head += "<th style='white-space:nowrap'>" + th_list[i] + "</th>"
    }
    tab.append($(head));

    var body = '';
    for (var i in data) {
        body += "<tr>";
        for (var j in data[i]) {
            var word_text = data[i][j];
            if (j > 0) {
                var word = word_text;
                if (word_text.indexOf("(") > 0) word = word_text.substring(0, word_text.indexOf("("));
                // var word_link = origin_url + "/words/detail?word=" + word;
                var word_link = "http://top.zhan.com/cihui/toefl-" + word + ".html";
                body += "<td style='white-space:nowrap'><a target='_blank' href='" + word_link + "'>" + word_text + "</a></td>";
            } else body += "<td style='white-space:nowrap'><b>" + word_text + "</b></td>";
        }
        body += "</tr>";
    }
    body = "<tbody>" + body + "</tbody>";
    tab.append($(body));
    $('body').append(tab);
    show_table_edit_button();
}

function show_add_words_nav() {
     //登录之后展示添加单词按钮
    $("#addWordsNav").css('display','block');
}

function hiden_add_words_nav() {
    //隐藏添加单词按钮
    $("#addWordsNav").css('display','none');
}

function show_table_edit_button() {
    //登录之后单词表格每列增加编辑按钮
    if($("#btnGroupDrop1").text() != "未登录"){
        $("thead tr").append("<th class='text-center' style='white-space:nowrap'>操作</th>");
        $("tbody tr").append("<td class='text-center'><div class='btn-group' role='group'>" +
            "<button type='button' class='btn btn-outline-info' name='wordEdit'>编辑</button>" +
            "<button type='button' class='btn btn-outline-danger' name='wordDelete'>删除</button>" +
            "</div></td>");
    }
    $("button[name='wordDelete']").click(submit_del_word);
    $("button[name='wordEdit']").click(show_words_edit_container);
}

function show_words_add_container () {
    // 添加单词窗口展开或关闭
    $("#container_add_word").html(default_word_container_html);
    if($("#container_add_word").css("display") == "none") $("#container_add_word").fadeIn("slow");
    else $("#container_add_word").fadeOut("fast");
    $("#AddEditSubmitButton").attr("onclick", "submit_add_word()");
    $("#AddEditSubmitButton").text("添加");
}

function show_words_edit_container() {
    // 编辑单词窗口展开或关闭
    $("#container_add_word").html(default_word_container_html);
    if($("#container_add_word").css("display") == "none") $("#container_add_word").fadeIn("slow");
    else $("#container_add_word").fadeOut("fast");

    var tr = $(this).parent().parent().parent();
    var row_data = get_word_row(tr);
    var meaning = row_data[0];
    var word_type = row_data[1];
    var words = row_data[2];

    $("#AddEditSubmitButton").attr("onclick", "submit_update_word('" + meaning + "', '" + word_type +"')");
    $("#AddEditSubmitButton").text("更新");
    $("html,body").animate({"scrollTop":top});

    $("#meaning").val(meaning);
    $('input:radio[value=' + word_type + ']').attr("checked", "true");
    if (words.length > 3){
        for (var i=0;i<words.length-3;i++){
            add_word_text();
        }}
    for(var i=0;i<words.length;i++){
        var word_text_id = "word_" + (i+1);
        $("#" + word_text_id).val(words[i]);
    }
}

function add_word_text() {
    //增加单词输入框
    var word_texts = document.getElementsByName("wrap_word_text");
    var last_word_text = word_texts[word_texts.length-1];

    var index = parseInt(last_word_text.id.split('_')[2]);
    var new_index = index + 1;
    var wrap_word_text_id = "word_text_" + new_index;
    var word_text_id = "word_" + new_index;
    var word_text_placeholder = "单词" + new_index;
    var btn_name = new_index + "";

    var new_html = $("#"+last_word_text.id).clone();

    new_html.find(":text").attr({"id": word_text_id, "placeholder": word_text_placeholder});
    new_html.find(":button").attr("name", btn_name);
    new_html.attr("id", wrap_word_text_id);
    new_html.appendTo($("#wrap_add_word"));
    $("#wrap_add_word").append("<br>")
}

function rem_word_text(text_id) {
    //删除单词输入框
    var word_texts = document.getElementsByName("wrap_word_text");
    if (word_texts.length < 2) 
    {
        alert("至少有一个单词");
        return
    }
    var wrap_word_text_id = "word_text_" + text_id;
    $("#"+wrap_word_text_id).next().remove();
    $("#"+wrap_word_text_id).remove();
}

function submit_add_word() {
    var meaning = $("#meaning").val();
    var word_type = $('input:radio[name=wordTypeRadio]:checked').val();
    if (!word_type){
        alert("请选择单词词性");
        return
    }
    var words = Array();
    $("input[name='word_text']").each(function () {
        if ($(this).val()) words.push($(this).val());
    });
    var js_param = JSON.stringify({
        "meaning": meaning,
        "word_type": word_type,
        "word_list": words
    });
    $.post("/words/synonym/add", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("添加成功！");
            $("#container_add_word").html(default_word_container_html);
            show_words_table(var_word_type);
            $("#container_add_word").fadeOut("fast");
        }
        else alert("添加失败：" + data["err_msg"]);
    })
}

function submit_del_word() {
    if (!confirm('确定要删除吗?')) return;
    var tr = $(this).parent().parent().parent();
    var row_data = get_word_row(tr);
    var meaning = row_data[0];
    var word_type = row_data[1]
    var words = row_data[2];
    var js_param = JSON.stringify({
        "meaning": meaning,
        "word_type": word_type,
        "word_list": words
    });
    $.post("/words/synonym/del", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("删除成功！");
            show_words_table(var_word_type);
        }
        else alert("删除失败：" + data["err_msg"]);
    })
}

function submit_update_word(old_meaning, old_word_type) {
    var meaning = $("#meaning").val();
    var word_type = $('input:radio[name=wordTypeRadio]:checked').val();
    if (!word_type){
        alert("请选择单词词性");
        return
    }
    var words = Array();
    $("input[name='word_text']").each(function () {
        if ($(this).val()) words.push($(this).val());
    });
    var js_param = JSON.stringify({
        "old_meaning": old_meaning,
        "old_word_type": old_word_type,
        "meaning": meaning,
        "word_type": word_type,
        "word_list": words
    });
    $.post("/words/synonym/mod", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("修改成功！");
            $("#container_add_word").html(default_word_container_html);
            show_words_table(var_word_type);
            $("#container_add_word").fadeOut("fast");
        }
        else alert("修改失败：" + data["err_msg"]);
    })
}

function get_word_row(tr) {
    var word_type = var_word_type;
    var meaning = "";
    var words = Array();
    var tds = tr.find("td");
    tds.each(function () {
        if ($(this).index() == tds.length -1) return;
        if ($(this).index() == 0) meaning = $(this).find("b").text();
        else {
            var word = $(this).find("a").text();
            if (var_word_type == "all") {
                words.push(word.substring(0, word.indexOf("(")));
                word_type = word.substring(word.indexOf("(")+1, word.indexOf(")"));
            }
            else words.push(word);
        }
    });
    return [meaning, word_type, words]
}

function export_excel(account_id) {
    var export_url = main_url + "file_export/statistics_xlsx";
    window.open(main_url + "file_export/statistics_xlsx?account_id=" + account_id + "&data=" + JSON.stringify(data_global));
}

