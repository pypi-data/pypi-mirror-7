// Compiled by ClojureScript 0.0-2234
goog.provide('tamarack.pages.all_apps');
goog.require('cljs.core');
goog.require('tamarack.xhr');
goog.require('sablono.core');
goog.require('tamarack.routes');
goog.require('sablono.core');
goog.require('tamarack.xhr');
goog.require('clojure.string');
goog.require('om.core');
goog.require('om.core');
goog.require('clojure.string');
goog.require('tamarack.routes');
tamarack.pages.all_apps.app_url = (function app_url(row){return tamarack.routes.url_of.cljs$core$IFn$_invoke$arity$2(tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$34,cljs.core.constant$keyword$48.cljs$core$IFn$_invoke$arity$1(row)], null));
});
tamarack.pages.all_apps.app_link_clicked = (function app_link_clicked(e,row){e.preventDefault();
return tamarack.routes.navigate_to.cljs$core$IFn$_invoke$arity$2(tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$34,cljs.core.constant$keyword$48.cljs$core$IFn$_invoke$arity$1(row)], null));
});
tamarack.pages.all_apps.render_row = (function render_row(row){return React.DOM.tr({"key": cljs.core.constant$keyword$48.cljs$core$IFn$_invoke$arity$1(row)},React.DOM.td(null,React.DOM.a({"href": tamarack.pages.all_apps.app_url(row), "onClick": (function (p1__7174_SHARP_){return tamarack.pages.all_apps.app_link_clicked(p1__7174_SHARP_,row);
})},sablono.interpreter.interpret(cljs.core.constant$keyword$123.cljs$core$IFn$_invoke$arity$1(row)))));
});
tamarack.pages.all_apps.page = (function page(app,owner){if(typeof tamarack.pages.all_apps.t7181 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.all_apps.t7181 = (function (owner,app,page,meta7182){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7182 = meta7182;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.all_apps.t7181.cljs$lang$type = true;
tamarack.pages.all_apps.t7181.cljs$lang$ctorStr = "tamarack.pages.all-apps/t7181";
tamarack.pages.all_apps.t7181.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"tamarack.pages.all-apps/t7181");
});
tamarack.pages.all_apps.t7181.prototype.om$core$IRender$ = true;
tamarack.pages.all_apps.t7181.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-8"},React.DOM.table({"className": "table table-hover table-striped"},React.DOM.thead(null,React.DOM.tr(null,React.DOM.th(null,"Application"))),(function (){var attrs7186 = cljs.core.map.cljs$core$IFn$_invoke$arity$2(tamarack.pages.all_apps.render_row,om.core.get_state.cljs$core$IFn$_invoke$arity$2(self__.owner,cljs.core.constant$keyword$130));return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(React.DOM.tbody,((cljs.core.map_QMARK_(attrs7186))?sablono.interpreter.attributes(attrs7186):null),cljs.core.remove(cljs.core.nil_QMARK_,((cljs.core.map_QMARK_(attrs7186))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret(attrs7186)], null))));
})())));
});
tamarack.pages.all_apps.t7181.prototype.om$core$IWillMount$ = true;
tamarack.pages.all_apps.t7181.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return tamarack.xhr.send_edn(new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$59,cljs.core.constant$keyword$56,cljs.core.constant$keyword$65,"/explorer-api/v1/applications",cljs.core.constant$keyword$63,((function (___$1){
return (function (res){return om.core.set_state_BANG_.cljs$core$IFn$_invoke$arity$3(self__.owner,cljs.core.constant$keyword$130,res);
});})(___$1))
], null));
});
tamarack.pages.all_apps.t7181.prototype.om$core$IDisplayName$ = true;
tamarack.pages.all_apps.t7181.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "AllApps";
});
tamarack.pages.all_apps.t7181.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7183){var self__ = this;
var _7183__$1 = this;return self__.meta7182;
});
tamarack.pages.all_apps.t7181.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7183,meta7182__$1){var self__ = this;
var _7183__$1 = this;return (new tamarack.pages.all_apps.t7181(self__.owner,self__.app,self__.page,meta7182__$1));
});
tamarack.pages.all_apps.__GT_t7181 = (function __GT_t7181(owner__$1,app__$1,page__$1,meta7182){return (new tamarack.pages.all_apps.t7181(owner__$1,app__$1,page__$1,meta7182));
});
}
return (new tamarack.pages.all_apps.t7181(owner,app,page,null));
});
