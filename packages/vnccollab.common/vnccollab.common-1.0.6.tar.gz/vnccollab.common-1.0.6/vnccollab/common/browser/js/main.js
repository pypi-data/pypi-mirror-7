// module definition
var vnc_collab_common = (function () {

  // Private components
  function initDeferredPortlets() {

    function deferredUrlInfo(elem) {
      var $elem = jq(elem);
      var manager = $elem.attr('portlet-manager');
      var name    = $elem.attr('portlet-name');
      var key     = $elem.attr('portlet-key');
      var id      = $elem.parent().attr('id');

      if (!manager || ! name || !key || !id) {
        return '';
      }

      return ({
        'url': window.location.origin + window.location.pathname + '/portlet_deferred_render',
        'data': {
          'manager': manager,
          'name': name,
          'key': key,
          'id': id
        }
      });
    }

    function updatePortlet(elem){
      // Returns a funciton to update the portlet represented by elem DOM
      var fn = function(data) {
        var $elem = jq(elem),
            $data = jq(data);

        // We want to be sure we got the portlet and not an error page
        if ($data.hasClass('portlet-deferred')) {
          $data.find('.portletBody').slimScroll({'height': '240px'});
          $elem.replaceWith($data);
        } else {
          $elem.find('.portletBodyWrapper').empty();
        }
      };
      return fn;
    }

    function deferredRender() {
      // Starts the deferred render of the portlet,
      // if it has enough info
      var urlInfo = deferredUrlInfo(this);
      if (!urlInfo) {
        return;
      }

      var url = urlInfo.url;
      var data = urlInfo.data;

      // Trigger DeferredPorletLoaded event if promise is complete
      jq.get(url, data, updatePortlet(this)).then(function(){
        jq('body').trigger( "DeferredPorletLoaded", data);
      });
    }

    var deferredPortlets = jq('.portlet-deferred');
    deferredPortlets.each(deferredRender);

  }

  // public interface
  return {
        initDeferredPortlets: initDeferredPortlets,
  };
}) ();


// run on load
jq(function() {
  var me = vnc_collab_common;
  me.initDeferredPortlets();
});
