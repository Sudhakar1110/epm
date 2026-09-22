function epms_badge(v){if(!v)return'';var s=String(v).toLowerCase(),c='epms-badge-info';if(['on track','excellent','very good','completed','a+','a','b+','b','gold','silver'].indexOf(s)>-1)c='epms-badge-success';else if(['needs attention','good','average','in progress','c','d'].indexOf(s)>-1)c='epms-badge-warning';else if(['at risk','needs improvement','blocked','f','fail'].indexOf(s)>-1)c='epms-badge-danger';else if(['pending'].indexOf(s)>-1)c='epms-badge-muted';return'<span class="epms-badge '+c+'">'+v+'</span>';}
function epms_progress(val){if(val===null||val===undefined||val==='')return'';var pct=parseFloat(String(val).replace('%',''))||0,c='blue';if(pct>=80)c='green';else if(pct>=60)c='yellow';else c='red';return'<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill '+c+'" style="width:'+Math.min(pct,100)+'%"></div></div><span class="epms-progress-label">'+pct.toFixed(1)+'%</span></div>';}
function epms_priority(v){if(!v)return'';var s=String(v).toLowerCase(),c='epms-priority-medium';if(s==='low')c='epms-priority-low';else if(s==='medium')c='epms-priority-medium';else if(s==='high')c='epms-priority-high';else if(s==='critical')c='epms-priority-critical';return'<span class="epms-priority '+c+'">'+v+'</span>';}
function epms_fmt(spec){setTimeout(function(){var t=document.querySelector('.page-wrapper table');if(!t)return;var hs=[];t.querySelectorAll('thead th').forEach(function(th){hs.push(th.textContent.trim().toLowerCase());});t.querySelectorAll('tbody tr').forEach(function(r){var cs=r.querySelectorAll('td');hs.forEach(function(h,i){if(spec[h]&&cs[i])cs[i].innerHTML=spec[h](cs[i].textContent.trim());});});},1500);}

frappe.query_reports['Daily Performance Report']={
    filters:[
        {fieldname:'date_from',fieldtype:'Date',label:__('From Date'),default:frappe.datetime.add_days(frappe.datetime.get_today(),-30),reqd:1},
        {fieldname:'date_to',fieldtype:'Date',label:__('To Date'),default:frappe.datetime.get_today(),reqd:1},
        {fieldname:'team',fieldtype:'Link',label:__('Team'),options:'Team'},
        {fieldname:'employee',fieldtype:'Link',label:__('Employee'),options:'Employee'},
        {fieldname:'priority',fieldtype:'Select',label:__('Priority'),options:'\nLow\nMedium\nHigh\nCritical'},
        {fieldname:'task_status',fieldtype:'Select',label:__('Status'),options:'\nCompleted\nIn Progress\nPending\nBlocked'}
    ],
    onload:function(r){epms_fmt({'priority':epms_priority,'status':epms_badge,'completion %':epms_progress});}
};
