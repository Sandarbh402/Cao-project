#!/usr/bin/env python3
"""
Cache Memory Performance Simulator — Tkinter GUI  (Redesigned)
Run:  python run_gui.py
"""
import os, sys, tkinter as tk
from tkinter import ttk, messagebox, filedialog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.module1_config    import CacheConfig
from modules.module5_analytics import run_simulation, export_csv, plot_comparison

BG=     "#12121e"; PANEL=  "#1c1c2e"; PANEL2= "#22223a"; CARD_BG="#1e1e32"
ACCENT= "#7c6af7"; ACCENT2="#38bdf8"; ACCENT3="#f472b6"
SUCCESS="#4ade80"; DANGER= "#f87171"; WARNING="#fbbf24"
TEXT=   "#e2e8f0"; SUBTEXT="#94a3b8"; MUTED=  "#475569"
BORDER= "#2e2e4a"; BORDER2="#3d3d5c"; ENTRY_BG="#252540"
BTN_BG= "#7c6af7"; BTN_HOV="#6d5ae6"; BTN_FG= "#ffffff"
HIT_ROW="#0d2e1a"; MISS_ROW="#2e0d1a"; HIT_FG= "#4ade80"; MISS_FG="#f87171"
FH1=("Segoe UI",14,"bold"); FH2=("Segoe UI",11,"bold"); FH3=("Segoe UI",9,"bold")
FB= ("Segoe UI",10);        FSM=("Segoe UI",9);          FXSM=("Segoe UI",8)
FMONO=("Consolas",9)

def _setup_styles():
    s=ttk.Style(); s.theme_use("clam")
    s.configure("Dark.TCombobox",fieldbackground=ENTRY_BG,background=ENTRY_BG,
                foreground=TEXT,selectbackground=ACCENT,selectforeground=BTN_FG,
                arrowcolor=ACCENT2,bordercolor=BORDER2,lightcolor=BORDER2,darkcolor=BORDER2)
    s.map("Dark.TCombobox",fieldbackground=[("readonly",ENTRY_BG)],foreground=[("readonly",TEXT)])
    s.configure("Trace.Treeview",background=CARD_BG,fieldbackground=CARD_BG,
                foreground=TEXT,rowheight=24,font=FMONO,borderwidth=0)
    s.configure("Trace.Treeview.Heading",background=PANEL2,foreground=ACCENT2,
                font=FH3,relief="flat",borderwidth=0,padding=(6,6))
    s.map("Trace.Treeview",background=[("selected","#3a3a5c")],foreground=[("selected",TEXT)])
    s.configure("Cmp.Treeview",background=CARD_BG,fieldbackground=CARD_BG,
                foreground=TEXT,rowheight=26,font=FB,borderwidth=0)
    s.configure("Cmp.Treeview.Heading",background=PANEL2,foreground=ACCENT2,
                font=FH3,relief="flat",borderwidth=0,padding=(6,6))
    s.configure("Dark.TNotebook",background=BG,borderwidth=0)
    s.configure("Dark.TNotebook.Tab",background=PANEL2,foreground=SUBTEXT,
                padding=[16,8],font=FB,borderwidth=0)
    s.map("Dark.TNotebook.Tab",background=[("selected",ACCENT)],foreground=[("selected",BTN_FG)])
    s.configure("TScrollbar",background=BORDER2,troughcolor=CARD_BG,
                arrowcolor=SUBTEXT,bordercolor=BORDER)

def lbl(p,text,font=FB,fg=TEXT,bg=None,**kw):
    return tk.Label(p,text=text,font=font,fg=fg,bg=bg or p.cget("bg"),**kw)

def ent(p,var,width=12,**kw):
    e=tk.Entry(p,textvariable=var,width=width,bg=ENTRY_BG,fg=TEXT,
               insertbackground=ACCENT2,relief="flat",font=FB,
               highlightbackground=BORDER2,highlightthickness=1,highlightcolor=ACCENT,**kw)
    e.bind("<FocusIn>", lambda ev:e.config(highlightbackground=ACCENT))
    e.bind("<FocusOut>",lambda ev:e.config(highlightbackground=BORDER2))
    return e

def cmb(p,values,var,width=18):
    return ttk.Combobox(p,values=values,textvariable=var,width=width,
                        state="readonly",style="Dark.TCombobox",font=FB)

def btt(p,text,cmd,bg=BTN_BG,fg=BTN_FG,pady=6,padx=14,font=None,width=None):
    b=tk.Button(p,text=text,command=cmd,bg=bg,fg=fg,activebackground=BTN_HOV,
                activeforeground=fg,relief="flat",font=font or("Segoe UI",10,"bold"),
                cursor="hand2",pady=pady,padx=padx)
    if width: b.config(width=width)
    b.bind("<Enter>",lambda e,_b=b,_h=BTN_HOV if bg==BTN_BG else bg:_b.config(bg=_h))
    b.bind("<Leave>",lambda e,_b=b,_bg=bg:_b.config(bg=_bg))
    return b

def hsep(p,c=BORDER2): return tk.Frame(p,bg=c,height=1)
def vsep(p,c=BORDER2): return tk.Frame(p,bg=c,width=1)

class CacheSimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cache Memory Performance Simulator")
        self.configure(bg=BG); self.resizable(True,True); self.minsize(1100,700)
        _setup_styles()
        self.all_runs=[]; self.last_result=None; self.last_cfg=None; self._rc=0
        self._init_vars(); self._build_ui(); self._center(1300,840)

    def _init_vars(self):
        self.v_cache_kb=tk.StringVar(value="4");  self.v_block_b=tk.StringVar(value="16")
        self.v_mapping =tk.StringVar(value="DIRECT"); self.v_assoc=tk.StringVar(value="4")
        self.v_policy  =tk.StringVar(value="LRU")
        self.v_hit_t   =tk.StringVar(value="1");  self.v_miss_p=tk.StringVar(value="100")
        self.v_run_lbl =tk.StringVar(value="")

    def _center(self,w,h):
        sw,sh=self.winfo_screenwidth(),self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        self._build_topbar(); self._build_main(); self._build_statusbar()

    # ── TOP BAR ──────────────────────────────────────────────────────
    def _build_topbar(self):
        bar=tk.Frame(self,bg=PANEL)
        bar.pack(fill="x")
        tk.Frame(bar,bg=ACCENT,width=4).pack(side="left",fill="y")
        left=tk.Frame(bar,bg=PANEL,padx=16,pady=12); left.pack(side="left")
        lbl(left,"⚡",font=("Segoe UI",18),fg=ACCENT,bg=PANEL).pack(side="left",padx=(0,8))
        t=tk.Frame(left,bg=PANEL); t.pack(side="left")
        lbl(t,"Cache Memory Performance Simulator",font=FH1,fg=TEXT,bg=PANEL).pack(anchor="w")
        lbl(t,"Computer Organisation & Architecture  ·  BITE301L",font=FSM,fg=SUBTEXT,bg=PANEL).pack(anchor="w")
        right=tk.Frame(bar,bg=PANEL,padx=16); right.pack(side="right",fill="y")
        for n,c in [("Romit Raman",ACCENT2),("Sandarbh Gupta",ACCENT),("Shivansh Verma",ACCENT3)]:
            lbl(right,f"● {n}",font=FXSM,fg=c,bg=PANEL).pack(anchor="e")
        hsep(self,BORDER).pack(fill="x")

    # ── MAIN (sidebar + content) ──────────────────────────────────────
    def _build_main(self):
        body=tk.Frame(self,bg=BG); body.pack(fill="both",expand=True)
        sidebar=tk.Frame(body,bg=PANEL,width=360)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        vsep(body).pack(side="left",fill="y")
        content=tk.Frame(body,bg=BG); content.pack(side="left",fill="both",expand=True)
        self._build_sidebar(sidebar); self._build_content(content)

    # ── SIDEBAR ──────────────────────────────────────────────────────
    def _build_sidebar(self,parent):
        canvas=tk.Canvas(parent,bg=PANEL,highlightthickness=0)
        sb=ttk.Scrollbar(parent,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); canvas.pack(side="left",fill="both",expand=True)
        inner=tk.Frame(canvas,bg=PANEL)
        wid=canvas.create_window((0,0),window=inner,anchor="nw")
        inner.bind("<Configure>",lambda e:(canvas.configure(scrollregion=canvas.bbox("all")),canvas.itemconfig(wid,width=canvas.winfo_width())))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(wid,width=e.width))
        inner.bind_all("<MouseWheel>",lambda e:canvas.yview_scroll(-int(e.delta/60),"units"))
        P=dict(padx=20)

        # ── [1] CACHE PARAMETERS ─────────────────────────────────────
        tk.Frame(inner,bg=PANEL,height=18).pack()
        self._sec_hdr(inner,"🗄  Cache Parameters",ACCENT2)
        tk.Frame(inner,bg=PANEL,height=10).pack()

        grid=tk.Frame(inner,bg=PANEL); grid.pack(fill="x",**P)
        grid.columnconfigure(0,weight=1); grid.columnconfigure(1,weight=1)

        for col,(name,hint,var) in enumerate([
            ("Cache Size","in KB",self.v_cache_kb),
            ("Block Size","bytes (power of 2)",self.v_block_b)]):
            f=tk.Frame(grid,bg=PANEL); f.grid(row=0,column=col,sticky="nsew",padx=(0,8 if col==0 else 0),pady=4)
            lbl(f,name,font=FH3,fg=TEXT,bg=PANEL).pack(anchor="w")
            lbl(f,hint,font=FXSM,fg=MUTED,bg=PANEL).pack(anchor="w",pady=(1,4))
            ent(f,var,width=10).pack(anchor="w",fill="x",expand=True)

        # ── [2] MAPPING TYPE ─────────────────────────────────────────
        tk.Frame(inner,bg=PANEL,height=16).pack()
        hsep(inner,BORDER2).pack(fill="x",**P)
        tk.Frame(inner,bg=PANEL,height=14).pack()
        self._sec_hdr(inner,"🗺  Mapping Type",ACCENT2)
        tk.Frame(inner,bg=PANEL,height=10).pack()

        mf=tk.Frame(inner,bg=PANEL); mf.pack(fill="x",**P)
        lbl(mf,"Mapping Strategy",font=FH3,fg=TEXT,bg=PANEL).pack(anchor="w")
        lbl(mf,"How memory blocks map to cache lines",font=FXSM,fg=MUTED,bg=PANEL).pack(anchor="w",pady=(2,6))
        cmb(mf,["DIRECT","FULLY_ASSOCIATIVE","SET_ASSOCIATIVE"],self.v_mapping,width=26).pack(anchor="w",fill="x")

        # Associativity (SA only)
        self._assoc_frame=tk.Frame(inner,bg=PANEL)
        af=self._assoc_frame
        af_inner=tk.Frame(af,bg=PANEL); af_inner.pack(fill="x",padx=20,pady=(10,0))
        lbl(af_inner,"Associativity (N-ways)",font=FH3,fg=TEXT,bg=PANEL).pack(anchor="w")
        lbl(af_inner,"e.g. 2 = 2-way, 4 = 4-way, 8 = 8-way",font=FXSM,fg=MUTED,bg=PANEL).pack(anchor="w",pady=(2,6))
        ent(af_inner,self.v_assoc,width=10).pack(anchor="w")
        self.v_mapping.trace_add("write",self._on_mapping_change)
        self._on_mapping_change()

        # ── [3] REPLACEMENT POLICY ───────────────────────────────────
        tk.Frame(inner,bg=PANEL,height=16).pack()
        hsep(inner,BORDER2).pack(fill="x",**P)
        tk.Frame(inner,bg=PANEL,height=14).pack()
        self._sec_hdr(inner,"♻  Replacement Policy",ACCENT2)
        tk.Frame(inner,bg=PANEL,height=4).pack()
        lbl(inner,"Select what to evict on a cache miss",font=FXSM,fg=MUTED,bg=PANEL).pack(anchor="w",padx=20,pady=(0,10))

        for val,title_text,desc,color in [
            ("FIFO",  "FIFO — First In First Out",  "Evicts the oldest loaded block",     WARNING),
            ("LRU",   "LRU  — Least Recently Used", "Evicts the least recently accessed", ACCENT2),
            ("RANDOM","RANDOM — Random Eviction",   "Evicts a randomly chosen block",     ACCENT3),
        ]:
            card=tk.Frame(inner,bg=CARD_BG,
                          highlightbackground=BORDER2,highlightthickness=1)
            card.pack(fill="x",padx=20,pady=4)
            ci=tk.Frame(card,bg=CARD_BG,padx=12,pady=10); ci.pack(fill="x")
            ci.columnconfigure(1,weight=1)

            rb=tk.Radiobutton(ci,variable=self.v_policy,value=val,
                              bg=CARD_BG,activebackground=CARD_BG,
                              selectcolor=color,fg=color,cursor="hand2",
                              relief="flat",bd=0)
            rb.grid(row=0,column=0,rowspan=2,sticky="ns",padx=(0,12))
            lbl(ci,title_text,font=FH3,fg=color,bg=CARD_BG).grid(row=0,column=1,sticky="w")
            lbl(ci,desc,font=FXSM,fg=SUBTEXT,bg=CARD_BG).grid(row=1,column=1,sticky="w",pady=(2,0))

            # click anywhere to select
            for w in (card,ci): w.bind("<Button-1>",lambda e,v=val:self.v_policy.set(v))
            for w in card.winfo_children(): w.bind("<Button-1>",lambda e,v=val:self.v_policy.set(v),"+")

        # ── [4] TIMING ───────────────────────────────────────────────
        tk.Frame(inner,bg=PANEL,height=16).pack()
        hsep(inner,BORDER2).pack(fill="x",**P)
        tk.Frame(inner,bg=PANEL,height=14).pack()
        self._sec_hdr(inner,"⏱  Timing Parameters",ACCENT2)
        tk.Frame(inner,bg=PANEL,height=4).pack()

        tbox=tk.Frame(inner,bg=CARD_BG,highlightbackground=BORDER2,highlightthickness=1)
        tbox.pack(fill="x",padx=20,pady=(4,0))
        ti=tk.Frame(tbox,bg=CARD_BG,padx=14,pady=10); ti.pack(fill="x")
        lbl(ti,"AMAT  =  Hit Time  +  (Miss Rate × Miss Penalty)",
            font=("Consolas",8),fg=MUTED,bg=CARD_BG).pack(anchor="w",pady=(0,10))

        tgrid=tk.Frame(ti,bg=CARD_BG); tgrid.pack(fill="x")
        tgrid.columnconfigure(0,weight=1); tgrid.columnconfigure(1,weight=1)
        for col,(name,hint,var) in enumerate([
            ("Hit Time","cycles",self.v_hit_t),
            ("Miss Penalty","cycles",self.v_miss_p)]):
            f=tk.Frame(tgrid,bg=CARD_BG); f.grid(row=0,column=col,sticky="nsew",padx=(0,8 if col==0 else 0))
            lbl(f,name,font=FH3,fg=TEXT,bg=CARD_BG).pack(anchor="w")
            lbl(f,hint,font=FXSM,fg=MUTED,bg=CARD_BG).pack(anchor="w",pady=(2,4))
            ent(f,var,width=8).pack(anchor="w")

        # ── [5] RUN LABEL + BUTTON ───────────────────────────────────
        tk.Frame(inner,bg=PANEL,height=16).pack()
        hsep(inner,BORDER2).pack(fill="x",**P)
        tk.Frame(inner,bg=PANEL,height=14).pack()

        rf=tk.Frame(inner,bg=PANEL); rf.pack(fill="x",**P)
        lbl(rf,"Run Label",font=FH3,fg=TEXT,bg=PANEL).pack(anchor="w")
        lbl(rf,"Optional — shown in Compare Runs table",font=FXSM,fg=MUTED,bg=PANEL).pack(anchor="w",pady=(2,6))
        ent(rf,self.v_run_lbl,width=28).pack(fill="x",expand=True)
        tk.Frame(inner,bg=PANEL,height=14).pack()

        run_btn=tk.Button(inner,text="▶   RUN SIMULATION",command=self._run,
                          bg=ACCENT,fg=BTN_FG,activebackground=BTN_HOV,
                          activeforeground=BTN_FG,relief="flat",
                          font=("Segoe UI",11,"bold"),cursor="hand2",pady=14)
        run_btn.pack(fill="x",padx=20)
        run_btn.bind("<Enter>",lambda e:run_btn.config(bg=BTN_HOV))
        run_btn.bind("<Leave>",lambda e:run_btn.config(bg=ACCENT))
        tk.Frame(inner,bg=PANEL,height=24).pack()

    def _sec_hdr(self,parent,text,color):
        f=tk.Frame(parent,bg=PANEL); f.pack(anchor="w",padx=20)
        lbl(f,text,font=FH2,fg=color,bg=PANEL).pack(side="left")

    def _on_mapping_change(self,*_):
        if self.v_mapping.get()=="SET_ASSOCIATIVE": self._assoc_frame.pack(fill="x")
        else: self._assoc_frame.pack_forget()

    # ── CONTENT AREA ─────────────────────────────────────────────────
    def _build_content(self,parent):
        self._build_addr_bar(parent)
        hsep(parent,BORDER).pack(fill="x")
        nb=ttk.Notebook(parent,style="Dark.TNotebook")
        nb.pack(fill="both",expand=True)
        t1=tk.Frame(nb,bg=BG); t2=tk.Frame(nb,bg=BG)
        t3=tk.Frame(nb,bg=BG); t4=tk.Frame(nb,bg=BG)
        nb.add(t1,text="  📋  Trace Table  ")
        nb.add(t2,text="  📊  Summary  ")
        nb.add(t3,text="  🔄  Compare Runs  ")
        nb.add(t4,text="  ℹ  Help  ")
        self._build_trace_tab(t1)
        self._build_summary_tab(t2)
        self._build_compare_tab(t3)
        self._build_help_tab(t4)

    def _build_addr_bar(self,parent):
        bar=tk.Frame(parent,bg=PANEL2); bar.pack(fill="x")
        top=tk.Frame(bar,bg=PANEL2,padx=14,pady=10); top.pack(fill="x")
        lbl(top,"📍  Memory Addresses",font=FH2,fg=ACCENT2,bg=PANEL2).pack(side="left")
        lbl(top,"  ·  one per line  ·  hex (0x1A3F) or decimal (6719)",
            font=FSM,fg=MUTED,bg=PANEL2).pack(side="left",padx=4)
        qf=tk.Frame(top,bg=PANEL2); qf.pack(side="right")
        lbl(qf,"Quick-fill:",font=FXSM,fg=SUBTEXT,bg=PANEL2).pack(side="left",padx=(0,4))
        for plabel,data in [
            ("Sequential","0x0000\n0x0010\n0x0020\n0x0030\n0x0040\n0x0050\n0x0060\n0x0070"),
            ("Conflict",  "0x0000\n0x1000\n0x2000\n0x0000\n0x1000\n0x2000\n0x0000\n0x1000"),
            ("Loop",      "0x0100\n0x0200\n0x0300\n0x0100\n0x0200\n0x0300\n0x0100\n0x0200"),
            ("Mixed",     "0x0000\n0x0010\n0x1000\n0x0000\n0x2000\n0x0010\n0x3000\n0x0000"),
        ]:
            def _fill(d=data): self.addr_text.delete("1.0","end"); self.addr_text.insert("1.0",d)
            b=tk.Button(qf,text=plabel,command=_fill,bg=BORDER2,fg=ACCENT2,
                        relief="flat",font=FXSM,cursor="hand2",padx=8,pady=3,
                        activebackground=ENTRY_BG,activeforeground=ACCENT2)
            b.pack(side="left",padx=2)
            b.bind("<Enter>",lambda e,_b=b:_b.config(bg=ENTRY_BG))
            b.bind("<Leave>",lambda e,_b=b:_b.config(bg=BORDER2))

        # FIXED PADY ISSUE HERE:
        tf=tk.Frame(bar,bg=PANEL2,padx=14); tf.pack(fill="x", pady=(0,10))
        bf=tk.Frame(tf,bg=BORDER2,padx=1,pady=1); bf.pack(fill="x")
        ti=tk.Frame(bf,bg=ENTRY_BG); ti.pack(fill="x")
        self.addr_text=tk.Text(ti,height=4,bg=ENTRY_BG,fg=TEXT,
                               insertbackground=ACCENT2,font=FMONO,
                               relief="flat",wrap="none",undo=True,
                               selectbackground="#3a3a5c",padx=10,pady=8)
        asb=ttk.Scrollbar(ti,orient="vertical",command=self.addr_text.yview)
        self.addr_text.configure(yscrollcommand=asb.set)
        self.addr_text.pack(side="left",fill="both",expand=True)
        asb.pack(side="right",fill="y")

    def _build_trace_tab(self,parent):
        tb=tk.Frame(parent,bg=BG,padx=10,pady=8); tb.pack(fill="x")
        lbl(tb,"Per-Access Trace",font=FH2,fg=TEXT,bg=BG).pack(side="left")
        leg=tk.Frame(tb,bg=BG); leg.pack(side="left",padx=16)
        for t,c in [("● HIT",HIT_FG),("● MISS",MISS_FG)]:
            lbl(leg,t,font=FSM,fg=c,bg=BG).pack(side="left",padx=6)
        btt(tb,"💾  Export CSV",self._export_csv,bg=BORDER2,fg=TEXT,pady=4,padx=12).pack(side="right",padx=4)
        btt(tb,"🗑  Clear",self._clear_trace,bg=BORDER2,fg=SUBTEXT,pady=4,padx=12).pack(side="right",padx=4)
        hsep(parent,BORDER).pack(fill="x")
        tf=tk.Frame(parent,bg=BG); tf.pack(fill="both",expand=True,padx=10,pady=8)
        tf.grid_rowconfigure(0,weight=1); tf.grid_columnconfigure(0,weight=1)
        cols=("No.","Address","Tag","Index","Offset","Result","Evicted")
        widths=(50,100,80,70,70,70,85)
        self.trace_tree=ttk.Treeview(tf,columns=cols,show="headings",style="Trace.Treeview")
        for c,w in zip(cols,widths):
            self.trace_tree.heading(c,text=c); self.trace_tree.column(c,width=w,anchor="center",minwidth=40)
        vsb=ttk.Scrollbar(tf,orient="vertical",command=self.trace_tree.yview)
        hsb=ttk.Scrollbar(tf,orient="horizontal",command=self.trace_tree.xview)
        self.trace_tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        self.trace_tree.grid(row=0,column=0,sticky="nsew")
        vsb.grid(row=0,column=1,sticky="ns"); hsb.grid(row=1,column=0,sticky="ew")
        self.trace_tree.tag_configure("hit", background=HIT_ROW, foreground=HIT_FG)
        self.trace_tree.tag_configure("miss",background=MISS_ROW,foreground=MISS_FG)

    def _build_summary_tab(self,parent):
        outer=tk.Frame(parent,bg=BG); outer.pack(fill="both",expand=True,padx=14,pady=12)
        cards_row=tk.Frame(outer,bg=BG); cards_row.pack(fill="x",pady=(0,12))
        self.stat_lbls={}
        for key,label_text,color,icon in [
            ("total","Total Accesses",TEXT,"🔢"),
            ("hits","Cache Hits",SUCCESS,"✅"),
            ("misses","Cache Misses",DANGER,"❌"),
            ("hit_ratio","Hit Ratio",ACCENT2,"📈"),
            ("miss_ratio","Miss Ratio",WARNING,"📉"),
            ("amat","AMAT (cycles)",ACCENT,"⏱"),
        ]:
            c=tk.Frame(cards_row,bg=CARD_BG,highlightbackground=BORDER2,highlightthickness=1)
            c.pack(side="left",fill="x",expand=True,padx=3)
            ci=tk.Frame(c,bg=CARD_BG,padx=10,pady=10); ci.pack(fill="both")
            tr=tk.Frame(ci,bg=CARD_BG); tr.pack(fill="x")
            lbl(tr,icon,font=("Segoe UI",12),fg=color,bg=CARD_BG).pack(side="left")
            lbl(tr,label_text,font=FXSM,fg=SUBTEXT,bg=CARD_BG).pack(side="left",padx=3)
            v=lbl(ci,"—",font=("Segoe UI",18,"bold"),fg=color,bg=CARD_BG)
            v.pack(anchor="w",pady=(4,0)); self.stat_lbls[key]=v

        detail=tk.Frame(outer,bg=BG); detail.pack(fill="both",expand=True)
        detail.columnconfigure(0,weight=1); detail.columnconfigure(1,weight=1)
        for (col,title_text,attr) in [(0,"⚙  Configuration","cfg_text"),(1,"♻  Eviction Summary","evict_text")]:
            box=tk.Frame(detail,bg=CARD_BG,highlightbackground=BORDER2,highlightthickness=1)
            box.grid(row=0,column=col,sticky="nsew",padx=(0,6) if col==0 else (6,0))
            lbl(box,title_text,font=FH2,fg=ACCENT2,bg=CARD_BG).pack(anchor="w",padx=14,pady=(12,4))
            hsep(box,BORDER2).pack(fill="x",padx=10)
            t=tk.Text(box,bg=CARD_BG,fg=TEXT,font=FMONO,relief="flat",
                      state="disabled",wrap="word",padx=14,pady=10,height=10)
            t.pack(fill="both",expand=True); setattr(self,attr,t)

    def _build_compare_tab(self,parent):
        tb=tk.Frame(parent,bg=BG,padx=10,pady=8); tb.pack(fill="x")
        lbl(tb,"Multi-Run Comparison",font=FH2,fg=TEXT,bg=BG).pack(side="left")
        btt(tb,"📊  Save Chart",self._save_chart,bg=ACCENT,pady=4,padx=12).pack(side="right",padx=4)
        btt(tb,"🗑  Clear All",self._clear_runs,bg=BORDER2,fg=SUBTEXT,pady=4,padx=12).pack(side="right",padx=4)
        hsep(parent,BORDER).pack(fill="x")
        lbl(parent,"  Run multiple simulations to compare configurations. Best hit ratio is highlighted green.",
            font=FSM,fg=SUBTEXT,bg=BG).pack(anchor="w",padx=10,pady=6)
        tf=tk.Frame(parent,bg=BG); tf.pack(fill="both",expand=True,padx=10,pady=(0,10))
        tf.grid_rowconfigure(0,weight=1); tf.grid_columnconfigure(0,weight=1)
        cols=("Label","Mapping","Policy","Assoc","Hits","Misses","Hit %","AMAT (cyc)")
        widths=(170,130,80,60,70,70,70,90)
        self.cmp_tree=ttk.Treeview(tf,columns=cols,show="headings",style="Cmp.Treeview")
        for c,w in zip(cols,widths):
            self.cmp_tree.heading(c,text=c); self.cmp_tree.column(c,width=w,anchor="center",minwidth=50)
        self.cmp_tree.column("Label",anchor="w")
        vsb=ttk.Scrollbar(tf,orient="vertical",command=self.cmp_tree.yview)
        hsb=ttk.Scrollbar(tf,orient="horizontal",command=self.cmp_tree.xview)
        self.cmp_tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        self.cmp_tree.grid(row=0,column=0,sticky="nsew")
        vsb.grid(row=0,column=1,sticky="ns"); hsb.grid(row=1,column=0,sticky="ew")
        self.cmp_tree.tag_configure("odd", background=CARD_BG)
        self.cmp_tree.tag_configure("even",background=PANEL2)
        self.cmp_tree.tag_configure("best",background="#1a2e1a",foreground=SUCCESS)

    def _build_help_tab(self,parent):
        canvas=tk.Canvas(parent,bg=BG,highlightthickness=0)
        sb=ttk.Scrollbar(parent,orient="vertical",command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right",fill="y"); canvas.pack(fill="both",expand=True)
        inner=tk.Frame(canvas,bg=BG,padx=30,pady=20)
        wid=canvas.create_window((0,0),window=inner,anchor="nw")
        inner.bind("<Configure>",lambda e:(canvas.configure(scrollregion=canvas.bbox("all"))))
        canvas.bind("<Configure>",lambda e:canvas.itemconfig(wid,width=e.width))
        sections=[
            ("📋  Inputs",ACCENT2,[
                ("Cache Size (KB)","Total cache memory. Common: 1, 4, 8, 16 KB."),
                ("Block Size (bytes)","One cache line size. Must be power of 2: 8,16,32,64…"),
                ("Mapping Type","DIRECT: 1 slot per block. FULLY_ASSOCIATIVE: any slot. SET_ASSOCIATIVE: N-way sets."),
                ("Associativity","Only for SA. Ways per set (2 = 2-way, 4 = 4-way, 8 = 8-way)."),
                ("Hit Time","Cycles to serve a hit from cache (typically 1-5)."),
                ("Miss Penalty","Extra cycles to fetch from RAM on a miss (typically 50-200)."),
                ("Memory Addresses","Hex (0x1A3F) or decimal (6719), one per line."),
            ]),
            ("♻  Policies",ACCENT,[
                ("FIFO","First In First Out — oldest loaded block is evicted first. Simple queue."),
                ("LRU","Least Recently Used — block not accessed longest is evicted. Best for loops."),
                ("RANDOM","Random eviction. No tracking overhead. Unpredictable performance."),
            ]),
            ("📐  Formulas",ACCENT3,[
                ("Hit Ratio","Hits ÷ Total × 100%"),
                ("Miss Ratio","Misses ÷ Total × 100%  (= 1 − Hit Ratio)"),
                ("AMAT","Hit Time + (Miss Rate × Miss Penalty)"),
                ("Offset bits","log₂(Block Size)  — byte within block"),
                ("Index bits","log₂(Number of Sets)  — which set"),
                ("Tag bits","Remaining address bits  — which memory block"),
            ]),
        ]
        for sec_title,color,items in sections:
            lbl(inner,sec_title,font=FH1,fg=color,bg=BG).pack(anchor="w",pady=(18,8))
            for it,desc in items:
                row=tk.Frame(inner,bg=CARD_BG,highlightbackground=BORDER2,highlightthickness=1)
                row.pack(fill="x",pady=3)
                ri=tk.Frame(row,bg=CARD_BG,padx=16,pady=10); ri.pack(fill="x")
                lbl(ri,it,font=FH3,fg=color,bg=CARD_BG).pack(anchor="w")
                lbl(ri,desc,font=FSM,fg=SUBTEXT,bg=CARD_BG,wraplength=680,justify="left").pack(anchor="w",pady=(3,0))

    def _build_statusbar(self):
        hsep(self,BORDER).pack(fill="x",side="bottom")
        self.status_var=tk.StringVar(value="Ready  —  configure the simulator and click RUN")
        bar=tk.Frame(self,bg=PANEL,pady=6); bar.pack(fill="x",side="bottom")
        tk.Frame(bar,bg=ACCENT,width=3).pack(side="left",fill="y",padx=(0,10))
        lbl(bar,"●",font=FSM,fg=SUCCESS,bg=PANEL).pack(side="left",padx=(0,6))
        lbl(bar,"",textvariable=self.status_var,font=FSM,fg=SUBTEXT,bg=PANEL).pack(side="left")

    # ── SIMULATION ────────────────────────────────────────────────────
    def _run(self):
        try:
            cache_kb=int(self.v_cache_kb.get()); block_b=int(self.v_block_b.get())
            mapping=self.v_mapping.get(); policy=self.v_policy.get()
            assoc=int(self.v_assoc.get()) if mapping=="SET_ASSOCIATIVE" else 1
            hit_t=int(self.v_hit_t.get()); miss_p=int(self.v_miss_p.get())
            cfg=CacheConfig(cache_kb,block_b,mapping,policy,assoc)
        except ValueError as e:
            messagebox.showerror("Configuration Error",str(e)); return

        lines=self.addr_text.get("1.0","end").strip().splitlines()
        addresses=[]
        for i,line in enumerate(lines,1):
            line=line.strip()
            if not line: continue
            try: addresses.append(int(line,16) if line.lower().startswith("0x") else int(line))
            except ValueError:
                messagebox.showerror("Address Error",f"Line {i}: cannot parse '{line}'\nUse 0x1A3F or integer.")
                return
        if not addresses:
            messagebox.showwarning("No Addresses","Enter at least one memory address."); return

        result=run_simulation(cfg,addresses,hit_t,miss_p)
        self.last_result=result; self.last_cfg=cfg; self._rc+=1
        self._populate_trace(result); self._populate_summary(cfg,result)
        label=self.v_run_lbl.get().strip() or f"Run {self._rc} · {mapping[:2]}/{policy}"
        self.all_runs.append((label,result,cfg))
        self._add_compare_row(label,cfg,result)
        self.status_var.set(f"✓  {label}  —  {result['hits']} hits / {result['misses']} misses  ·  "
                            f"Hit ratio: {result['hit_ratio']*100:.1f}%  ·  AMAT: {result['amat']:.2f} cycles")
        self.v_run_lbl.set("")

    def _populate_trace(self,result):
        self.trace_tree.delete(*self.trace_tree.get_children())
        for r in result['trace']:
            tag="hit" if r['result']=="HIT" else "miss"
            self.trace_tree.insert("","end",tags=(tag,),
                values=(r['access_no'],r['address'],r['tag'],r['index'],r['offset'],r['result'],r['evicted']))

    def _populate_summary(self,cfg,result):
        for key,val in [("total",str(result['total'])),("hits",str(result['hits'])),
                        ("misses",str(result['misses'])),
                        ("hit_ratio",f"{result['hit_ratio']*100:.1f}%"),
                        ("miss_ratio",f"{result['miss_ratio']*100:.1f}%"),
                        ("amat",f"{result['amat']:.2f}")]:
            self.stat_lbls[key].config(text=val)
        def _write(w,t):
            w.config(state="normal"); w.delete("1.0","end"); w.insert("1.0",t); w.config(state="disabled")
        _write(self.cfg_text,cfg.summary())
        _write(self.evict_text,result['tracker'].policy_summary())

    def _add_compare_row(self,label,cfg,result):
        tag="odd" if len(self.all_runs)%2==1 else "even"
        m={"DIRECT":"DIRECT","FULLY_ASSOCIATIVE":"FULLY ASSOC","SET_ASSOCIATIVE":"SET ASSOC"}.get(cfg.mapping_type,cfg.mapping_type)
        self.cmp_tree.insert("","end",tags=(tag,),
            values=(label,m,cfg.policy,cfg.associativity,result['hits'],result['misses'],
                    f"{result['hit_ratio']*100:.1f}%",f"{result['amat']:.2f}"))
        self._highlight_best()

    def _highlight_best(self):
        best_id=None; best=-1
        for iid in self.cmp_tree.get_children():
            r=float(self.cmp_tree.item(iid,"values")[6].replace("%",""))
            if r>best: best=r; best_id=iid
        for i,iid in enumerate(self.cmp_tree.get_children()):
            self.cmp_tree.item(iid,tags=("best" if iid==best_id else ("odd" if i%2==0 else "even"),))

    def _clear_trace(self): self.trace_tree.delete(*self.trace_tree.get_children())
    def _clear_runs(self):
        self.all_runs.clear(); self._rc=0
        self.cmp_tree.delete(*self.cmp_tree.get_children())
        self.status_var.set("Compare list cleared.")

    def _export_csv(self):
        if not self.last_result: messagebox.showinfo("No Data","Run a simulation first."); return
        path=filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files","*.csv"),("All files","*.*")],initialfile="cache_trace.csv")
        if path: export_csv(self.last_result,path); self.status_var.set(f"✓  CSV exported → {path}")

    def _save_chart(self):
        if not self.all_runs: messagebox.showinfo("No Data","Run at least one simulation first."); return
        path=filedialog.asksaveasfilename(defaultextension=".png",
            filetypes=[("PNG image","*.png"),("All files","*.*")],initialfile="comparison.png")
        if path:
            out=plot_comparison([(r[0],r[1]) for r in self.all_runs],filepath=path)
            if out: self.status_var.set(f"✓  Chart saved → {path}")
            else: messagebox.showerror("Error","matplotlib not installed.\npip install matplotlib")

if __name__=="__main__":
    app=CacheSimApp(); app.mainloop()