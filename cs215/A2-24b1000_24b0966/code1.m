im11=double(imread("T1.jpg"));
im22=double(imread("T2.jpg"));
P=zeros(1,21);
QMI = zeros(1, 21); % Initialize Q to store results for each t
MI = zeros(1, 21); % Initialize MI to store mutual information values

for t=-10:10
    im_22=zeros(532,460);
    if t>=0
for i=t+1:460
    im_22((1:532),i)=im22((1:532),i-t);
end
im1=im11(1:532,1+t:460);
im_2=im_22(1:532,1+t:460);
    else 
for i=1:460+t
    im_22((1:532),i)=im22((1:532),i-t);
end
im1=im11(1:532,1:460+t);
im_2=im_22(1:532,1:460+t);
    end
p=corrcoef(im1(:),im_2(:));
P(1,t+11)=p(1,2);
s=double(0);
B=unique(im1(:));
A=B(2:256,1:1);
M1=zeros(1,255);
M2=zeros(1,255);
x=size(A,1);
M=zeros(26,26);
sum=double(0);
sum1=double(0);
for a=1:10:251
    for b=1:10:251
        if a==251
            i=find(im1>=A(a,1) & im1<=A(255,1));
        else
        i=find(im1>=A(a,1) & im1<A(a+10,1));
        end
        if b==251
            j=find(im_2>=A(b,1) & im_2<=A(255,1));
        else
            j=find(im_2>=A(b,1) & im_2<A(b+10,1));
        end
        k=double(intersect(i,j));
        c=size(k,1);
        M(floor(a/10)+1,floor(b/10)+1) = c; 
    end
end
    for a=1:26
        for b=1:26
            s=s+M(a,b);
        end
    end 
 M=M./s;
 for a=1:26
     for b=1:26
         M1(1,a)=M1(1,a)+M(a,b);
         M2(1,a)=M2(1,a)+M(b,a);
     end
 end

 for a=1:26
     for b=1:26
         sum=sum+(M(a,b)-M1(1,a)*M2(1,b))^2;
         if M(a,b)~=0
         sum1=sum1+M(a,b)*log(M(a,b)/(M1(1,a)*M2(1,b)));
         end
     end
 end
QMI(1,t+11)=sum;
MI(1,t+11)=sum1;
end
x = -10:10;

figure;
plot(x, P, 'b-o','LineWidth',1.5);
xlabel('Shift (t)');
ylabel('Correlation');
title('1 Correlation vs Shift');
grid on;
saveas(gcf, '1 Correlation_vs_Shift.png');   


figure;
plot(x, QMI, 'r-s','LineWidth',1.5);
xlabel('Shift (t)');
ylabel('Quadratic MI');
title('1 Quadratic Mutual Information vs Shift');
grid on;
saveas(gcf, '1 QMI_vs_Shift.png');

figure;
plot(x, MI, 'g-^','LineWidth',1.5);
xlabel('Shift (t)');
ylabel('Mutual Information');
title('1 Mutual Information vs Shift');
grid on;
saveas(gcf, '1 MI_vs_Shift.png');
