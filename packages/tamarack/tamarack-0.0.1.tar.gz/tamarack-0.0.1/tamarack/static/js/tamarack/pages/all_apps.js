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
tamarack.pages.all_apps.app_url = (function app_url(row){return tamarack.routes.url_of.call(null,tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"id","id",1013907597),new cljs.core.Keyword(null,"name","name",1017277949).cljs$core$IFn$_invoke$arity$1(row)], null));
});
tamarack.pages.all_apps.app_link_clicked = (function app_link_clicked(e,row){e.preventDefault();
return tamarack.routes.navigate_to.call(null,tamarack.routes.app_dashboard,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"id","id",1013907597),new cljs.core.Keyword(null,"name","name",1017277949).cljs$core$IFn$_invoke$arity$1(row)], null));
});
tamarack.pages.all_apps.render_row = (function render_row(row){return React.DOM.tr({"key": new cljs.core.Keyword(null,"name","name",1017277949).cljs$core$IFn$_invoke$arity$1(row)},React.DOM.td(null,React.DOM.a({"href": tamarack.pages.all_apps.app_url.call(null,row), "onClick": (function (p1__7174_SHARP_){return tamarack.pages.all_apps.app_link_clicked.call(null,p1__7174_SHARP_,row);
})},sablono.interpreter.interpret.call(null,new cljs.core.Keyword(null,"display-name","display-name",2582814760).cljs$core$IFn$_invoke$arity$1(row)))));
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
tamarack.pages.all_apps.t7181.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write.call(null,writer__4141__auto__,"tamarack.pages.all-apps/t7181");
});
tamarack.pages.all_apps.t7181.prototype.om$core$IRender$ = true;
tamarack.pages.all_apps.t7181.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-8"},React.DOM.table({"className": "table table-hover table-striped"},React.DOM.thead(null,React.DOM.tr(null,React.DOM.th(null,"Application"))),(function (){var attrs7186 = cljs.core.map.call(null,tamarack.pages.all_apps.render_row,om.core.get_state.call(null,self__.owner,new cljs.core.Keyword(null,"applications","applications",1951111317)));return cljs.core.apply.call(null,React.DOM.tbody,((cljs.core.map_QMARK_.call(null,attrs7186))?sablono.interpreter.attributes.call(null,attrs7186):null),cljs.core.remove.call(null,cljs.core.nil_QMARK_,((cljs.core.map_QMARK_.call(null,attrs7186))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret.call(null,attrs7186)], null))));
})())));
});
tamarack.pages.all_apps.t7181.prototype.om$core$IWillMount$ = true;
tamarack.pages.all_apps.t7181.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return tamarack.xhr.send_edn.call(null,new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"method","method",4231316563),new cljs.core.Keyword(null,"get","get",1014006472),new cljs.core.Keyword(null,"url","url",1014020321),"/explorer-api/v1/applications",new cljs.core.Keyword(null,"on-complete","on-complete",2943599833),((function (___$1){
return (function (res){return om.core.set_state_BANG_.call(null,self__.owner,new cljs.core.Keyword(null,"applications","applications",1951111317),res);
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

//# sourceMappingURL=all_apps.js.map