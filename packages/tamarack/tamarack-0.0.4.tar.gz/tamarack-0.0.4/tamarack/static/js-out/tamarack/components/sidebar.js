// Compiled by ClojureScript 0.0-2234
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
tamarack.components.sidebar.app_items = (function app_items(view,app){return React.DOM.ol(null,React.DOM.li({"className": ((cljs.core._EQ_.call(null,view,new cljs.core.Keyword(null,"app-dashboard","app-dashboard",3494823258)))?"active":null)},React.DOM.a({"href": clojure.string.join.call(null,"/",new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, ["#/applications",new cljs.core.Keyword(null,"name","name",1017277949).cljs$core$IFn$_invoke$arity$1(app)], null))},"Dashboard")));
});
tamarack.components.sidebar.component = (function component(app,owner){if(typeof tamarack.components.sidebar.t7009 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.components.sidebar.t7009 = (function (owner,app,component,meta7010){
this.owner = owner;
this.app = app;
this.component = component;
this.meta7010 = meta7010;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.components.sidebar.t7009.cljs$lang$type = true;
tamarack.components.sidebar.t7009.cljs$lang$ctorStr = "tamarack.components.sidebar/t7009";
tamarack.components.sidebar.t7009.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write.call(null,writer__4141__auto__,"tamarack.components.sidebar/t7009");
});
tamarack.components.sidebar.t7009.prototype.om$core$IRender$ = true;
tamarack.components.sidebar.t7009.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var G__7012 = (((new cljs.core.Keyword(null,"view","view",1017523735).cljs$core$IFn$_invoke$arity$1(self__.app) instanceof cljs.core.Keyword))?new cljs.core.Keyword(null,"view","view",1017523735).cljs$core$IFn$_invoke$arity$1(self__.app).fqn:null);switch (G__7012) {
case "app-endpoint-overview":
return tamarack.components.sidebar.app_items.call(null,new cljs.core.Keyword(null,"view","view",1017523735).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-app","current-app",1613970239).cljs$core$IFn$_invoke$arity$1(self__.app));

break;
case "app-dashboard":
return tamarack.components.sidebar.app_items.call(null,new cljs.core.Keyword(null,"view","view",1017523735).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-app","current-app",1613970239).cljs$core$IFn$_invoke$arity$1(self__.app));

break;
case "all-apps":
return tamarack.components.sidebar.all_apps_items.call(null);

break;
default:
return React.DOM.ol(null);

}
});
tamarack.components.sidebar.t7009.prototype.om$core$IDisplayName$ = true;
tamarack.components.sidebar.t7009.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Sidebar";
});
tamarack.components.sidebar.t7009.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7011){var self__ = this;
var _7011__$1 = this;return self__.meta7010;
});
tamarack.components.sidebar.t7009.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7011,meta7010__$1){var self__ = this;
var _7011__$1 = this;return (new tamarack.components.sidebar.t7009(self__.owner,self__.app,self__.component,meta7010__$1));
});
tamarack.components.sidebar.__GT_t7009 = (function __GT_t7009(owner__$1,app__$1,component__$1,meta7010){return (new tamarack.components.sidebar.t7009(owner__$1,app__$1,component__$1,meta7010));
});
}
return (new tamarack.components.sidebar.t7009(owner,app,component,null));
});

//# sourceMappingURL=sidebar.js.map