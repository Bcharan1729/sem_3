x=[2:1:100];
y=1-((1./x).^(1./x));
[~,idx]=max(y);
k=x(idx);
display(k);
display(y(idx));