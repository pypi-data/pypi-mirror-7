$(function() {
   var NoteModel = Backbone.Model.extend({
     idAttribute: "key",
     initialize: function() {
       this.set("colors", {
         "TODO": "danger",
         "XXX": "info",
         "FIXME": "success"
        });
     }
   });

   var Notes = Backbone.Collection.extend({
     model: NoteModel,

     url: '/api/v1/' + project_id + '/todo/state',

     message: function(data) {
       this.remove(this.get(data.key));
       switch (data.type) {
           case "created":
           case "modified":
             this.add(new NoteModel(data));
             break;
           default:
             break;
       }
     },

     comparator: function(chapter) {
           return chapter.get("key");
     }

   });

   var NotesRouter = Backbone.Router.extend({
     routes: {
         "notes": "notes"
     }
   });

   var NotesApp = Backbone.View.extend({
     el: "#row1",

     initialize: function() {
       var this_ = this;
       this.listenTo(this.model, "add", this.render);
       this.listenTo(this.model, "remove", this.render);

       $.get("/plugins/todo/widget.html", function(template){
         this_.template = _.template(template);
         this_.model.fetch().done(function() { this_.render() });
       });

       window.app.subscribe('todo',
                            {'project': project_id, 'plugin': 'todo'},
                            function(data){ this_.model.message(data) });
     },
 
     render: function() { 
       this.$el.html(this.template({'states': this.model.toJSON()}));

       $(".todo-list").sortable({
         placeholder: "sort-highlight",
         handle: ".handle",
         forcePlaceholderSize: true,
         zIndex: 999999
       }).disableSelection();

       /* The todo list plugin */
       $(".todo-list").todolist({
         onCheck: function(ele) {
           console.log("The element has been checked")
         },
         onUncheck: function(ele) {
           console.log("The element has been unchecked")
         }
       });

       return this;
     } 

   });

   var App = new NotesApp({model: new Notes()});
});
