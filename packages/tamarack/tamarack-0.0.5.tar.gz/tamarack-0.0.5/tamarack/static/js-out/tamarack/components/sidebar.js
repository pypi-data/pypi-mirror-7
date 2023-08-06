// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.components.sidebar');
goog.require('cljs.core');
goog.require('sablono.core');
goog.require('sablono.core');
goog.require('clojure.string');
goog.require('clojure.string');
goog.require('om.core');
goog.require('om.core');
tamarack.components.sidebar.all_apps_items = (function all_apps_items(){return React.DOM.ol(null,React.DOM.li({"className": "active"},React.DOM.a({"href": "#"},"Applications")));
});
tamarack.components.sidebar.app_items = (function app_items(view,app){return React.DOM.ol(null,React.DOM.li({"className": ((cljs.core._EQ_.call(null,view,new cljs.core.Keyword(null,"app-dashboard","app-dashboard",-106677937)))?"active":null)},React.DOM.a({"href": clojure.string.join.call(null,"/",new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, ["#/applications",new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(app)], null))},"Dashboard")));
});
tamarack.components.sidebar.component = (function component(app,owner){if(typeof tamarack.components.sidebar.t7058 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.components.sidebar.t7058 = (function (owner,app,component,meta7059){
this.owner = owner;
this.app = app;
this.component = component;
this.meta7059 = meta7059;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.components.sidebar.t7058.cljs$lang$type = true;
tamarack.components.sidebar.t7058.cljs$lang$ctorStr = "tamarack.components.sidebar/t7058";
tamarack.components.sidebar.t7058.cljs$lang$ctorPrWriter = (function (this__4145__auto__,writer__4146__auto__,opt__4147__auto__){return cljs.core._write.call(null,writer__4146__auto__,"tamarack.components.sidebar/t7058");
});
tamarack.components.sidebar.t7058.prototype.om$core$IRender$ = true;
tamarack.components.sidebar.t7058.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var G__7061 = (((new cljs.core.Keyword(null,"view","view",1247994814).cljs$core$IFn$_invoke$arity$1(self__.app) instanceof cljs.core.Keyword))?new cljs.core.Keyword(null,"view","view",1247994814).cljs$core$IFn$_invoke$arity$1(self__.app).fqn:null);switch (G__7061) {
case "app-endpoint-overview":
return tamarack.components.sidebar.app_items.call(null,new cljs.core.Keyword(null,"view","view",1247994814).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app));

break;
case "app-dashboard":
return tamarack.components.sidebar.app_items.call(null,new cljs.core.Keyword(null,"view","view",1247994814).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app));

break;
case "all-apps":
return tamarack.components.sidebar.all_apps_items.call(null);

break;
default:
return React.DOM.ol(null);

}
});
tamarack.components.sidebar.t7058.prototype.om$core$IDisplayName$ = true;
tamarack.components.sidebar.t7058.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Sidebar";
});
tamarack.components.sidebar.t7058.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7060){var self__ = this;
var _7060__$1 = this;return self__.meta7059;
});
tamarack.components.sidebar.t7058.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7060,meta7059__$1){var self__ = this;
var _7060__$1 = this;return (new tamarack.components.sidebar.t7058(self__.owner,self__.app,self__.component,meta7059__$1));
});
tamarack.components.sidebar.__GT_t7058 = (function __GT_t7058(owner__$1,app__$1,component__$1,meta7059){return (new tamarack.components.sidebar.t7058(owner__$1,app__$1,component__$1,meta7059));
});
}
return (new tamarack.components.sidebar.t7058(owner,app,component,null));
});

//# sourceMappingURL=sidebar.js.map