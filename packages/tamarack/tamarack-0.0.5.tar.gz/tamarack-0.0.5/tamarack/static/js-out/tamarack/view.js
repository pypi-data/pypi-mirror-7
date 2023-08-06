// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.view');
goog.require('cljs.core');
goog.require('tamarack.components.debug');
goog.require('tamarack.components.timeslice');
goog.require('tamarack.pages.main');
goog.require('tamarack.state');
goog.require('tamarack.util');
goog.require('tamarack.util');
goog.require('tamarack.components.sidebar');
goog.require('tamarack.components.debug');
goog.require('tamarack.state');
goog.require('tamarack.components.sidebar');
goog.require('om.core');
goog.require('om.core');
goog.require('tamarack.pages.main');
goog.require('tamarack.components.timeslice');
tamarack.view.render_all = (function render_all(){om.core.root.call(null,tamarack.pages.main.page,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"target","target",253001721),tamarack.util.element_by_id.call(null,"main-content")], null));
om.core.root.call(null,tamarack.components.sidebar.component,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"target","target",253001721),tamarack.util.element_by_id.call(null,"sidebar")], null));
om.core.root.call(null,tamarack.components.timeslice.nav_label,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"target","target",253001721),tamarack.util.element_by_id.call(null,"timeslice-nav"),new cljs.core.Keyword(null,"path","path",-188191168),new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929)], null)], null));
om.core.root.call(null,tamarack.components.timeslice.edit_tracking_now_duration,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"target","target",253001721),tamarack.util.element_by_id.call(null,"up-to-now-tab"),new cljs.core.Keyword(null,"path","path",-188191168),new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929)], null)], null));
om.core.root.call(null,tamarack.components.timeslice.edit_date_range,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"target","target",253001721),tamarack.util.element_by_id.call(null,"date-range-tab"),new cljs.core.Keyword(null,"path","path",-188191168),new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.Keyword(null,"timeslice","timeslice",446627929)], null)], null));
var temp__4126__auto__ = tamarack.util.element_by_id.call(null,"debug-container");if(cljs.core.truth_(temp__4126__auto__))
{var debug_container = temp__4126__auto__;return om.core.root.call(null,tamarack.components.debug.component,tamarack.state.app_state,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"target","target",253001721),debug_container], null));
} else
{return null;
}
});

//# sourceMappingURL=view.js.map