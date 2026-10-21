"""Optional diagnostic plots."""
from pathlib import Path
def save_fit_plot(x,y,result,*,x_label,y_label,output_path,title="Linear fit and residuals"):
    try: import matplotlib.pyplot as plt
    except ImportError as e: raise RuntimeError("Install Matplotlib to generate plots.") from e
    p=Path(output_path); p.parent.mkdir(parents=True,exist_ok=True); order=sorted(range(len(x)),key=lambda i:x[i])
    fig,(a,b)=plt.subplots(2,1,figsize=(7.2,6.4),sharex=True,gridspec_kw={"height_ratios":[3,1]})
    a.scatter(x,y,label="Observed data"); a.plot([x[i] for i in order],[result.fitted[i] for i in order],label="Linear fit")
    a.set_ylabel(y_label); a.set_title(title); a.legend(); a.grid(True,alpha=.25)
    b.axhline(0); b.scatter(x,result.residuals); b.set_xlabel(x_label); b.set_ylabel("Residual"); b.grid(True,alpha=.25)
    fig.tight_layout(); fig.savefig(p,dpi=180,bbox_inches="tight"); plt.close(fig); return p
