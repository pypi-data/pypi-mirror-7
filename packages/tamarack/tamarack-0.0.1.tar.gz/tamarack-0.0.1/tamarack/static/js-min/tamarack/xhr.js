// Compiled by ClojureScript 0.0-2234
goog.provide('tamarack.xhr');
goog.require('cljs.core');
goog.require('goog.events.EventType');
goog.require('goog.net.XhrIo');
goog.require('goog.events');
goog.require('goog.events');
goog.require('cljs.reader');
goog.require('cljs.reader');
tamarack.xhr.meths = new cljs.core.PersistentArrayMap(null, 4, [cljs.core.constant$keyword$56,"GET",cljs.core.constant$keyword$61,"PUT",cljs.core.constant$keyword$57,"POST",cljs.core.constant$keyword$62,"DELETE"], null);
tamarack.xhr.send_edn = (function send_edn(p__7280){var map__7282 = p__7280;var map__7282__$1 = ((cljs.core.seq_QMARK_(map__7282))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__7282):map__7282);var on_complete = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7282__$1,cljs.core.constant$keyword$63);var data = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7282__$1,cljs.core.constant$keyword$64);var url = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7282__$1,cljs.core.constant$keyword$65);var method = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7282__$1,cljs.core.constant$keyword$59);var xhr = (new goog.net.XhrIo());goog.events.listen(xhr,goog.net.EventType.COMPLETE,((function (xhr,map__7282,map__7282__$1,on_complete,data,url,method){
return (function (e){return (on_complete.cljs$core$IFn$_invoke$arity$1 ? on_complete.cljs$core$IFn$_invoke$arity$1(cljs.reader.read_string(xhr.getResponseText())) : on_complete.call(null,cljs.reader.read_string(xhr.getResponseText())));
});})(xhr,map__7282,map__7282__$1,on_complete,data,url,method))
);
return xhr.send(url,(tamarack.xhr.meths.cljs$core$IFn$_invoke$arity$1 ? tamarack.xhr.meths.cljs$core$IFn$_invoke$arity$1(method) : tamarack.xhr.meths.call(null,method)),(cljs.core.truth_(data)?cljs.core.pr_str.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([data], 0)):null),{"Accept": "application/edn"});
});
