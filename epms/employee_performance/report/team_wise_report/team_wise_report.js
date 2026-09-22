function epms_progress(val){if(val===null||val===undefined||val==='')return'';var pct=parseFloat(String(val).replace('%',''))||0,c='blue';if(pct>=80)c='green';else if(pct>=60)c='yellow';else c='red';return'<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill '+c+'" style="width:'+Math.min(pct,100)+'%"></div></div><span class="epms-progress-label">'+pct.toFixed(1)+'%</span></div>';}
function epms_score(v){if(v===null||v===undefined||v==='')return'0';var n=parseFloat(v)||0,c='epms-badge-success';if(n<60)c='epms-badge-danger';else if(n<80)c='epms-badge-warning';return'<span class="epms-badge '+c+'">'+n.toFixed(1)+'</span>';}
function epms_fmt(spec){setTimeout(function(){var t=document.querySelector('.page-wrapper table');if(!t)return;var hs=[];t.querySelectorAll('thead th').forEach(function(th){hs.push(th.textContent.trim().toLowerCase());});t.querySelectorAll('tbody tr').forEach(function(r){var cs=r.querySelectorAll('td');hs.forEach(function(h,i){if(spec[h]&&cs[i])cs[i].innerHTML=spec[h](cs[i].textContent.trim());});});},1500);}

frappe.query_reports['Team Wise Report']={
    filters:[
        {fieldname:'date_from',fieldtype:'Date',label:__('From Date'),default:frappe.datetime.add_days(frappe.datetime.get_today(),-30),reqd:1},
        {fieldname:'date_to',fieldtype:'Date',label:__('To Date'),default:frappe.datetime.get_today(),reqd:1}
    ],
    onload:function(r){epms_fmt({'avg completion %':epms_progress,'team score':epms_score});}
};
