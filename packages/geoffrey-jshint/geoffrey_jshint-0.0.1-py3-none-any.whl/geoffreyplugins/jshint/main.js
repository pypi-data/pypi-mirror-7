$(function() {

   window.app.subscribe(
       'jshint',  // The name of this subscription.
       {  // The subscription criteria.
        'project': project_id,  // Global variable `project_id`
        'plugin': 'jshint'
       },
       function(data) {
         // This callback is called when an event that match with this
         // subscription arrives.
         console.dir(data)
       }
   );

});