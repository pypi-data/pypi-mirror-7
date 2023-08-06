// Compiled by ClojureScript 0.0-2234
goog.provide('tamarack.components.breadcrumbs');
goog.require('cljs.core');
goog.require('tamarack.xhr');
goog.require('tamarack.xhr');
goog.require('tamarack.routes');
goog.require('tamarack.routes');
goog.require('sablono.core');
goog.require('sablono.core');
goog.require('om.core');
goog.require('om.core');
tamarack.components.breadcrumbs.make_location_list = (function make_location_list(app){var pred__6986 = cljs.core._EQ_;var expr__6987 = cljs.core.constant$keyword$112.cljs$core$IFn$_invoke$arity$1(app);if(cljs.core.truth_((pred__6986.cljs$core$IFn$_invoke$arity$2 ? pred__6986.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$117,expr__6987) : pred__6986.call(null,cljs.core.constant$keyword$117,expr__6987))))
{return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,"Applications",cljs.core.constant$keyword$65,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.routes.all_apps], null)], null),new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,cljs.core.constant$keyword$123.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app)),cljs.core.constant$keyword$65,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$34,cljs.core.constant$keyword$99.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app))], null)], null)], null),new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,cljs.core.constant$keyword$116.cljs$core$IFn$_invoke$arity$1(app),cljs.core.constant$keyword$65,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.routes.app_endpoint_overview,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$34,cljs.core.constant$keyword$99.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app)),cljs.core.constant$keyword$115,cljs.core.constant$keyword$116.cljs$core$IFn$_invoke$arity$1(app)], null)], null)], null)], null);
} else
{if(cljs.core.truth_((pred__6986.cljs$core$IFn$_invoke$arity$2 ? pred__6986.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$114,expr__6987) : pred__6986.call(null,cljs.core.constant$keyword$114,expr__6987))))
{return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,"Applications",cljs.core.constant$keyword$65,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.routes.all_apps], null)], null),new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,cljs.core.constant$keyword$123.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app)),cljs.core.constant$keyword$65,new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$34,cljs.core.constant$keyword$99.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app))], null)], null)], null)], null);
} else
{if(cljs.core.truth_((pred__6986.cljs$core$IFn$_invoke$arity$2 ? pred__6986.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$113,expr__6987) : pred__6986.call(null,cljs.core.constant$keyword$113,expr__6987))))
{return new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$124,"Applications",cljs.core.constant$keyword$65,tamarack.routes.all_apps()], null)], null);
} else
{throw (new Error(("No matching clause: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(expr__6987))));
}
}
}
});
tamarack.components.breadcrumbs.goto_location = (function goto_location(url,e){e.preventDefault();
return cljs.core.apply.cljs$core$IFn$_invoke$arity$2(tamarack.routes.navigate_to,url);
});
tamarack.components.breadcrumbs.fetch_app_name_if_missing = (function fetch_app_name_if_missing(app){if(cljs.core.truth_((function (){var and__3561__auto__ = cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app);if(cljs.core.truth_(and__3561__auto__))
{return cljs.core.not(cljs.core.constant$keyword$123.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app)));
} else
{return and__3561__auto__;
}
})()))
{return tamarack.xhr.send_edn(new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$59,cljs.core.constant$keyword$56,cljs.core.constant$keyword$65,("/explorer-api/v1/applications/"+cljs.core.str.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$99.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(app)))),cljs.core.constant$keyword$63,(function (res){return om.core.transact_BANG_.cljs$core$IFn$_invoke$arity$3(app,cljs.core.constant$keyword$98,cljs.core.partial.cljs$core$IFn$_invoke$arity$2(cljs.core.merge,res));
})], null));
} else
{return null;
}
});
tamarack.components.breadcrumbs.component = (function component(app,owner){if(typeof tamarack.components.breadcrumbs.t6994 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.components.breadcrumbs.t6994 = (function (owner,app,component,meta6995){
this.owner = owner;
this.app = app;
this.component = component;
this.meta6995 = meta6995;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.components.breadcrumbs.t6994.cljs$lang$type = true;
tamarack.components.breadcrumbs.t6994.cljs$lang$ctorStr = "tamarack.components.breadcrumbs/t6994";
tamarack.components.breadcrumbs.t6994.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"tamarack.components.breadcrumbs/t6994");
});
tamarack.components.breadcrumbs.t6994.prototype.om$core$IRender$ = true;
tamarack.components.breadcrumbs.t6994.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var location_list = tamarack.components.breadcrumbs.make_location_list(self__.app);var make_location_elem = ((function (location_list,___$1){
return (function (i,loc){var is_active = cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2((i + 1),cljs.core.count(location_list));var map__6997 = loc;var map__6997__$1 = ((cljs.core.seq_QMARK_(map__6997))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__6997):map__6997);var url = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__6997__$1,cljs.core.constant$keyword$65);var title = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__6997__$1,cljs.core.constant$keyword$124);return new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$43,((is_active)?new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$28,"active"], null):null),((is_active)?title:new cljs.core.PersistentVector(null, 3, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.constant$keyword$41,new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$39,"#",cljs.core.constant$keyword$122,cljs.core.partial.cljs$core$IFn$_invoke$arity$2(tamarack.components.breadcrumbs.goto_location,url)], null),title], null))], null);
});})(location_list,___$1))
;var attrs6998 = cljs.core.map_indexed(make_location_elem,location_list);return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(React.DOM.ol,((cljs.core.map_QMARK_(attrs6998))?sablono.interpreter.attributes(sablono.util.merge_with_class.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$28,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, ["breadcrumb"], null)], null),attrs6998], 0))):{"className": "breadcrumb"}),cljs.core.remove(cljs.core.nil_QMARK_,((cljs.core.map_QMARK_(attrs6998))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret(attrs6998)], null))));
});
tamarack.components.breadcrumbs.t6994.prototype.om$core$IWillUpdate$ = true;
tamarack.components.breadcrumbs.t6994.prototype.om$core$IWillUpdate$will_update$arity$3 = (function (_,next_props,___$1){var self__ = this;
var ___$2 = this;return tamarack.components.breadcrumbs.fetch_app_name_if_missing(next_props);
});
tamarack.components.breadcrumbs.t6994.prototype.om$core$IWillMount$ = true;
tamarack.components.breadcrumbs.t6994.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return tamarack.components.breadcrumbs.fetch_app_name_if_missing(self__.app);
});
tamarack.components.breadcrumbs.t6994.prototype.om$core$IDisplayName$ = true;
tamarack.components.breadcrumbs.t6994.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Breadcrumbs";
});
tamarack.components.breadcrumbs.t6994.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_6996){var self__ = this;
var _6996__$1 = this;return self__.meta6995;
});
tamarack.components.breadcrumbs.t6994.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_6996,meta6995__$1){var self__ = this;
var _6996__$1 = this;return (new tamarack.components.breadcrumbs.t6994(self__.owner,self__.app,self__.component,meta6995__$1));
});
tamarack.components.breadcrumbs.__GT_t6994 = (function __GT_t6994(owner__$1,app__$1,component__$1,meta6995){return (new tamarack.components.breadcrumbs.t6994(owner__$1,app__$1,component__$1,meta6995));
});
}
return (new tamarack.components.breadcrumbs.t6994(owner,app,component,null));
});
