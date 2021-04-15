var data = {
    generatePageDataLocal: {
        generatePostAddr: "/model/generate_post",
        commentResponse: null,
        imageBinary: null,
        tags: null,
    }
};

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}


var demo = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: data,
    methods: {
        getResponseSuccess(data){
            this.generatePageDataLocal.commentResponse = data;

            $("#animation").css("display", "none");

            this.generatePageDataLocal.tags = null;

            $("textarea").val(data["message"])
        },

        getFileRawDataHandler(e) {
            this.generatePageDataLocal.imageBinary = btoa(e.target.result)
        },

        setFileHandler(e){
            $("#preview").css("display", "block");

            var fileName = e.target.files[0].name;
            var f = document.getElementById("FileD");

            $("#FileInput").val(fileName);

            var reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById("preview").src = e.target.result;
            };
            reader.readAsDataURL(f.files[0]);

            var reader = new FileReader();
            reader.onload = this.getFileRawDataHandler

            reader.readAsBinaryString(f.files[0])
        },

        startTimer(){
            if (!this.generatePageDataLocal.tags){
                var tags = $("#TagsInput").val()
                console.log(tags)
                if (!tags) {
                    return
                }

                this.generatePageDataLocal.tags = [];
                var tag_list = tags.split(" ");

                for (e in tag_list){
                    if (tag_list[e]){
                        this.generatePageDataLocal.tags.push(tag_list[e])
                    }
                }
            }

            var el = $("#animation");
            el.css("display", "flex");

            console.log(this.generatePageDataLocal.imageBinary)
            $.ajax({
                type: "POST",
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    "tags": this.generatePageDataLocal.tags,
                    "image": this.generatePageDataLocal.imageBinary
                }),
                url: this.generatePageDataLocal.generatePostAddr,
                async: false,
                success: this.getResponseSuccess,
                error: function (){
                    console.log("govno")
                }
            });
        },
    },

    mounted(){
            $("input:file").change(this.setFileHandler);
            $(document).on("click", ".browse", function() {
                var file = $(this).parents().find(".file");
                file.trigger("click");
            });
        }
});


