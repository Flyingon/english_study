
function titles_show () {
    $.get('/words/listen/titles', function (data, status) {
        var items = data;
        app_title = new Vue({
            el: '#app-listen-tiltes',
            data: {
                fixed: true,
                items: items,
                fields: [
                    {key: 'id', label: '索引', sortable: true},
                    {key: 'title_en', label: '文章名', sortable: true},
                    {key: 'title_cn', label: '翻译'},
                    {key: 'source', label: 'TPO', sortable: true},
                    {key: 'pic', label: '图片'}
                ],
                totalRows: items.length,
                filter: null
            },
            computed: {
                sortOptions() {
                    // Create an options list from our fields
                    return this.fields
                        .filter(f => f.sortable)
                        .map(f => {
                            return {text: f.label, value: f.key}
                        })
                }
            },
            methods: {
                onFiltered: function (filteredItems) {
                    // Trigger pagination to update the number of buttons/pages due to filtering
                    this.totalRows = filteredItems.length
                }
            }
        })
    });
}

function words_show () {
    $.get('/words/listen/words?id=' + GetParamString('id'), function (data, status) {
        var items = data;
        app_word = new Vue({
            el: '#app-listen-words',
            data: {
                fixed: true,
                items: items,
                fields: [
                    {key: 'word_en', label: '单词', sortable: true},
                    {key: 'word_cn', label: '释义'},
                    {key: 'id', thStyle: "display:none", tdAttr: {style: "display:none"}},
                ],
                totalRows: items.length,
                filter: null,
            },
            computed: {
                sortOptions() {
                    // Create an options list from our fields
                    return this.fields
                        .filter(f => f.sortable)
                        .map(f => {
                            return {text: f.label, value: f.key}
                        })
                }
            },
            methods: {
                onFiltered: function (filteredItems) {
                    // Trigger pagination to update the number of buttons/pages due to filtering
                    this.totalRows = filteredItems.length
                }
            },
            mounted: function () {
                this.$nextTick(function () {
                    showAddEditBtn()
                })
            },
            updated: function () {
                this.$nextTick(function () {
                    showAddEditBtn()
                })
            }
        })
    });
}

function refresh_words() {
    $.get('/words/listen/words?id=' + GetParamString('id'), function (data, status) {
        app_word.items = data;
    })
}

function showAddEditBtn() {
     //登录之后展示添加编辑按钮
    showEditBtn();
    showAddBtn();
}

function showAddBtn () {
    // 根据登录状态隐藏或显示添加单词按钮
    if($("#btnGroupDrop1").text() != "未登录") $("#add-word-nav").css('display','block');
    else $("#add-word-nav").css('display','none');
}

function showEditBtn () {
    //登录之后单词表格每列增加编辑按钮
    if($("#btnGroupDrop1").text() != "未登录"){
        $("#app-listen-words thead tr").each(function () {
            var ths = $(this).find("th");
            if($(ths[ths.length-1]).text() != '操作') $(this).append($("<th class='text-center' style='white-space:nowrap'>操作</th>"));
        });
        $("#app-listen-words tbody tr").each(function () {
            var tds = $(this).find("td");
            if (!tds.has("button[name='wordDelete']").length && !tds.has("button[name='wordEdit']").length) {
            $(this).append($("<td class='text-center'><div class='btn-group' role='group'>" +
                "<button type='button' class='btn btn-outline-info' name='wordEdit'>编辑</button>" +
                "<button type='button' class='btn btn-outline-danger' name='wordDelete'>删除</button>" +
                "</div></td>"))}
        })
    }
    $("button[name='wordDelete']").click(submitDel);
    $("button[name='wordEdit']").click(showEditContainer);
}

function showAddContainer () {
    // 添加单词窗口展开或关闭
    $("#word").val("");
    $("#meaning").val("");
    var elment = $("#app-listen-add-word");
    if(elment.css("display") == "none") elment.fadeIn("slow");
    else elment.fadeOut("fast");
    $("#add-edit-submit-btn").attr("onclick", "submitAddWord()");
    $("#add-edit-submit-btn").text("添加");
}

function showEditContainer() {
    // 编辑单词窗口展开或关闭
    var elment = $("#app-listen-add-word");
    if(elment.css("display") == "none") elment.fadeIn("slow");
    else elment.fadeOut("fast");

    var tr = $(this).parent().parent().parent();
    var tds = tr.find("td");
    var word = $(tds[0]).text();
    var meaning = $(tds[1]).text();
    var word_id = $(tds[2]).text();

    $("#add-edit-submit-btn").attr("onclick", "submitUpdateWord('" + word_id +"')");
    $("#add-edit-submit-btn").text("更新");
    $("html,body").animate({"scrollTop":top});

    $("#word").val(word);
    $("#meaning").val(meaning);
}


function submitAddWord() {
    var word = $("#word").val();
    var meaning = $("#meaning").val();

    var js_param = JSON.stringify({
        "listen_id": GetParamString("id"),
        "word": word,
        "meaning": meaning,
    });
    $.post("/words/listen/add", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("添加成功！");
            refresh_words();
            $("#app-listen-add-word").fadeOut("fast");
        }
        else alert("添加失败：" + data["err_msg"]);
    })
}

function submitDel() {
    if (!confirm('确定要删除吗?')) return;
    var tr = $(this).parent().parent().parent();
    var tds = tr.find("td");
    var word_id = $(tds[2]).text();
    var js_param = JSON.stringify({
        "word_id": word_id,
    });
    $.post("/words/listen/del", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("删除成功！");
            refresh_words();
        }
        else alert("删除失败：" + data["err_msg"]);
    })
}

function submitUpdateWord(word_id) {
    var word = $("#word").val();
    var meaning = $("#meaning").val();

    var js_param = JSON.stringify({
        "word_id": word_id,
        "word": word,
        "meaning": meaning,
    });
    $.post("/words/listen/update", js_param, function (data, status) {
        if (data["err_code"] == 0) {
            alert("修改成功！");
            refresh_words();
            $("#app-listen-add-word").fadeOut("fast");
        }
        else alert("修改失败：" + data["err_msg"]);
    })
}
