.class public final Lcom/example/myschedule/MainActivity;
.super Landroidx/activity/ComponentActivity;
.source "MainActivity.kt"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/example/myschedule/MainActivity$Companion;
    }
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\"\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0004\u0008\u0007\u0018\u0000 \u000c2\u00020\u0001:\u0001\u000cB\u0005\u00a2\u0006\u0002\u0010\u0002J\u0008\u0010\u0005\u001a\u00020\u0006H\u0002J\u0012\u0010\u0007\u001a\u00020\u00062\u0008\u0010\u0008\u001a\u0004\u0018\u00010\tH\u0014J\u0008\u0010\n\u001a\u00020\u0006H\u0014J\u0008\u0010\u000b\u001a\u00020\u0006H\u0014R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082.\u00a2\u0006\u0002\n\u0000\u00a8\u0006\r"
    }
    d2 = {
        "Lcom/example/myschedule/MainActivity;",
        "Landroidx/activity/ComponentActivity;",
        "()V",
        "vm",
        "Lcom/example/myschedule/viewmodel/MainViewModel;",
        "askNotificationPermission",
        "",
        "onCreate",
        "savedInstanceState",
        "Landroid/os/Bundle;",
        "onPause",
        "onResume",
        "Companion",
        "app_release"
    }
    k = 0x1
    mv = {
        0x1,
        0x9,
        0x0
    }
    xi = 0x30
.end annotation


# static fields
.field public static final $stable:I

.field public static final Companion:Lcom/example/myschedule/MainActivity$Companion;

.field public static final REQ_NOTIFY:I = 0x3e9


# instance fields
.field private vm:Lcom/example/myschedule/viewmodel/MainViewModel;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lcom/example/myschedule/MainActivity$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lcom/example/myschedule/MainActivity$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lcom/example/myschedule/MainActivity;->Companion:Lcom/example/myschedule/MainActivity$Companion;

    const/16 v0, 0x8

    sput v0, Lcom/example/myschedule/MainActivity;->$stable:I

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 25
    invoke-direct {p0}, Landroidx/activity/ComponentActivity;-><init>()V

    return-void
.end method

.method public static final synthetic access$getVm$p(Lcom/example/myschedule/MainActivity;)Lcom/example/myschedule/viewmodel/MainViewModel;
    .locals 0

    .line 25
    iget-object p0, p0, Lcom/example/myschedule/MainActivity;->vm:Lcom/example/myschedule/viewmodel/MainViewModel;

    return-object p0
.end method

.method private final askNotificationPermission()V
    .locals 4

    .line 82
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x21

    if-lt v0, v1, :cond_0

    .line 83
    move-object v0, p0

    check-cast v0, Landroid/content/Context;

    const-string v1, "android.permission.POST_NOTIFICATIONS"

    invoke-static {v0, v1}, Landroidx/core/content/ContextCompat;->checkSelfPermission(Landroid/content/Context;Ljava/lang/String;)I

    move-result v0

    if-eqz v0, :cond_0

    .line 85
    move-object v0, p0

    check-cast v0, Landroid/app/Activity;

    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/String;

    const/4 v3, 0x0

    aput-object v1, v2, v3

    const/16 v1, 0x3e9

    invoke-static {v0, v2, v1}, Landroidx/core/app/ActivityCompat;->requestPermissions(Landroid/app/Activity;[Ljava/lang/String;I)V

    :cond_0
    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 7

    .line 30
    invoke-super {p0, p1}, Landroidx/activity/ComponentActivity;->onCreate(Landroid/os/Bundle;)V

    .line 32
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    const/4 v0, 0x0

    invoke-static {p1, v0}, Landroidx/core/view/WindowCompat;->setDecorFitsSystemWindows(Landroid/view/Window;Z)V

    .line 34
    move-object p1, p0

    check-cast p1, Lcom/example/myschedule/MainActivity;

    .line 35
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/view/Window;->setStatusBarColor(I)V

    .line 36
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/view/Window;->setNavigationBarColor(I)V

    .line 38
    sget p1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1d

    if-lt p1, v1, :cond_0

    .line 39
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/view/Window;->setStatusBarContrastEnforced(Z)V

    .line 40
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    invoke-virtual {p1, v0}, Landroid/view/Window;->setNavigationBarContrastEnforced(Z)V

    .line 42
    :cond_0
    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object p1

    const/16 v0, 0x10

    invoke-virtual {p1, v0}, Landroid/view/Window;->setSoftInputMode(I)V

    .line 44
    new-instance p1, Landroidx/lifecycle/ViewModelProvider;

    move-object v0, p0

    check-cast v0, Landroidx/lifecycle/ViewModelStoreOwner;

    invoke-direct {p1, v0}, Landroidx/lifecycle/ViewModelProvider;-><init>(Landroidx/lifecycle/ViewModelStoreOwner;)V

    const-class v0, Lcom/example/myschedule/viewmodel/MainViewModel;

    invoke-virtual {p1, v0}, Landroidx/lifecycle/ViewModelProvider;->get(Ljava/lang/Class;)Landroidx/lifecycle/ViewModel;

    move-result-object p1

    check-cast p1, Lcom/example/myschedule/viewmodel/MainViewModel;

    iput-object p1, p0, Lcom/example/myschedule/MainActivity;->vm:Lcom/example/myschedule/viewmodel/MainViewModel;

    invoke-virtual {p0}, Lcom/example/myschedule/MainActivity;->getIntent()Landroid/content/Intent;

    move-result-object v1

    const-string v2, "login_user"

    invoke-virtual {v1, v2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    const-string v3, "login_pwd"

    invoke-virtual {v1, v3}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    if-eqz v2, :no_login_extra

    if-eqz v3, :no_login_extra

    const/4 v4, 0x1

    invoke-virtual {p1, v2, v3, v4}, Lcom/example/myschedule/viewmodel/MainViewModel;->saveAccount(Ljava/lang/String;Ljava/lang/String;Z)V

    invoke-virtual {p1, v4}, Lcom/example/myschedule/viewmodel/MainViewModel;->loginAndRefresh(Z)V

    :no_login_extra

    .line 45
    sget-object p1, Lcom/example/myschedule/sync/SyncScheduler;->INSTANCE:Lcom/example/myschedule/sync/SyncScheduler;

    move-object v0, p0

    check-cast v0, Landroid/content/Context;

    invoke-virtual {p1, v0}, Lcom/example/myschedule/sync/SyncScheduler;->ensureScheduled(Landroid/content/Context;)V

    .line 46
    sget-object p1, Lcom/example/myschedule/sync/PlanSyncAlarm;->INSTANCE:Lcom/example/myschedule/sync/PlanSyncAlarm;

    invoke-virtual {p1, v0}, Lcom/example/myschedule/sync/PlanSyncAlarm;->schedule(Landroid/content/Context;)V

    .line 47
    sget-object p1, Lcom/example/myschedule/notify/PunchReminder;->INSTANCE:Lcom/example/myschedule/notify/PunchReminder;

    invoke-virtual {p1, v0}, Lcom/example/myschedule/notify/PunchReminder;->ensureChannel(Landroid/content/Context;)V

    .line 48
    invoke-direct {p0}, Lcom/example/myschedule/MainActivity;->askNotificationPermission()V

    .line 50
    new-instance p1, Lcom/example/myschedule/ui/NavState;

    invoke-direct {p1}, Lcom/example/myschedule/ui/NavState;-><init>()V

    .line 51
    move-object v0, p0

    check-cast v0, Landroidx/activity/ComponentActivity;

    new-instance v1, Lcom/example/myschedule/MainActivity$onCreate$2;

    invoke-direct {v1, p0, p1}, Lcom/example/myschedule/MainActivity$onCreate$2;-><init>(Lcom/example/myschedule/MainActivity;Lcom/example/myschedule/ui/NavState;)V

    const p1, -0x7b034132

    const/4 v2, 0x1

    invoke-static {p1, v2, v1}, Landroidx/compose/runtime/internal/ComposableLambdaKt;->composableLambdaInstance(IZLjava/lang/Object;)Landroidx/compose/runtime/internal/ComposableLambda;

    move-result-object p1

    check-cast p1, Lkotlin/jvm/functions/Function2;

    const/4 v1, 0x0

    invoke-static {v0, v1, p1, v2, v1}, Landroidx/activity/compose/ComponentActivityKt;->setContent$default(Landroidx/activity/ComponentActivity;Landroidx/compose/runtime/CompositionContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)V

    return-void
.end method

.method protected onPause()V
    .locals 1

    .line 77
    sget-object v0, Lcom/example/myschedule/util/AppVisible;->INSTANCE:Lcom/example/myschedule/util/AppVisible;

    invoke-virtual {v0}, Lcom/example/myschedule/util/AppVisible;->onPause()V

    .line 78
    invoke-super {p0}, Landroidx/activity/ComponentActivity;->onPause()V

    return-void
.end method

.method protected onResume()V
    .locals 1

    .line 71
    invoke-super {p0}, Landroidx/activity/ComponentActivity;->onResume()V

    .line 72
    sget-object v0, Lcom/example/myschedule/util/AppVisible;->INSTANCE:Lcom/example/myschedule/util/AppVisible;

    invoke-virtual {v0}, Lcom/example/myschedule/util/AppVisible;->onResume()V

    .line 73
    iget-object v0, p0, Lcom/example/myschedule/MainActivity;->vm:Lcom/example/myschedule/viewmodel/MainViewModel;

    if-nez v0, :cond_0

    const-string v0, "vm"

    invoke-static {v0}, Lkotlin/jvm/internal/Intrinsics;->throwUninitializedPropertyAccessException(Ljava/lang/String;)V

    const/4 v0, 0x0

    :cond_0
    invoke-virtual {v0}, Lcom/example/myschedule/viewmodel/MainViewModel;->onResume()V

    return-void
.end method
