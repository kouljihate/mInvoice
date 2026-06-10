import flet as ft
from app.fe.mobile.widgets.theme import PRIMARY, SECONDARY, CARD_BG, TEXT_SECONDARY, ERROR, SUCCESS, WARNING, border_all
from app.shared.utils import tr_static


def dashboard_view(page, navigate):
    company = page.db.get_company()
    currency = (company.currency + " ") if company else "MAD "
    d = page.db.get_dashboard_data()

    def logout(e):
        page.session.store.set("user_id", None); navigate("/login")

    def kpi_card(title, value, icon, color, route=None):
        lighter = color + "18"
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                    bgcolor=color, padding=8, border_radius=10,
                    shadow=ft.BoxShadow(blur_radius=8, color=color + "40", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=10),
                ft.Text(title, size=11, color="#94A3B8", height=14),
                ft.Text(value, size=17, weight=ft.FontWeight.BOLD, color="#1E293B", height=22),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=14, top=12, right=14, bottom=14),
            bgcolor=ft.Colors.WHITE, border_radius=14, ink=True,
            on_click=lambda e: navigate(route) if route else None, expand=True,
            shadow=ft.BoxShadow(blur_radius=12, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
        )

    def section_card(title, icon, icon_color, *children):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=18, color=ft.Colors.WHITE),
                        bgcolor=icon_color, padding=8, border_radius=10,
                        shadow=ft.BoxShadow(blur_radius=8, color=icon_color + "40", offset=ft.Offset(0, 2)),
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#1E293B", text_align=ft.TextAlign.CENTER),
                ft.Container(height=12),
                *children,
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
            padding=ft.Padding(left=14, top=12, right=14, bottom=14), bgcolor=ft.Colors.WHITE, border_radius=14,
            shadow=ft.BoxShadow(blur_radius=12, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
            expand=True,
        )

    def nav_card(title, icon, color, route):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=22, color=ft.Colors.WHITE),
                    bgcolor=color, padding=10, border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=8, color=color + "40", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=8),
                ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color="#1E293B", height=16, text_align=ft.TextAlign.CENTER),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, top=12, right=10, bottom=12),
            bgcolor=ft.Colors.WHITE, border_radius=14, ink=True,
            on_click=lambda e: navigate(route), expand=True,
            shadow=ft.BoxShadow(blur_radius=12, color="rgba(0,0,0,0.06)", offset=ft.Offset(0, 2)),
        )

    def signal_item(label, value, color):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=13, color="#475569", expand=True),
                ft.Container(
                    content=ft.Text(str(value), size=12, weight=ft.FontWeight.BOLD, color=color),
                    padding=ft.Padding(left=8, top=2, right=8, bottom=2),
                    bgcolor=color + "15",
                    border_radius=6,
                ),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=4, top=2, right=4, bottom=2),
        )

    def progress_bar(label, value, max_val, color, suffix=""):
        pct = min(value / max_val * 100, 100) if max_val > 0 else 0
        return ft.Column([
            ft.Row([
                ft.Text(label, size=12, color="#475569", expand=True),
                ft.Text(f"{suffix}{value:,.0f}", size=12, weight=ft.FontWeight.BOLD, color="#1E293B"),
            ], spacing=4),
            ft.Container(
                content=ft.Container(
                    height=6, bgcolor=color, border_radius=3,
                ),
                width=pct * 3, bgcolor=color + "18", border_radius=3, height=6,
                animate=ft.animation.Animation(600, "easeOut"),
            ),
        ], spacing=4)

    rows_data = [
        (tr_static(page.session.store.get("lang", "en"), "sales_month"), f"{currency}{d['sales_month']:,.0f}", ft.Icons.TRENDING_UP, "#2563EB", "/payments"),
        (tr_static(page.session.store.get("lang", "en"), "invoiced_month"), f"{currency}{d['invoiced_month']:,.0f}", ft.Icons.RECEIPT, "#7C3AED", "/invoices"),
        (tr_static(page.session.store.get("lang", "en"), "paid_month"), f"{currency}{d['paid_month']:,.0f}", ft.Icons.CHECK_CIRCLE, "#059669", "/payments"),
        (tr_static(page.session.store.get("lang", "en"), "outstanding"), f"{currency}{d['outstanding']:,.0f}", ft.Icons.HOURGLASS_EMPTY, "#D97706", "/invoices"),
        (tr_static(page.session.store.get("lang", "en"), "overdue"), f"{d['overdue_count']} ({currency}{d['overdue_amount']:,.0f})", ft.Icons.WARNING_AMBER, "#DC2626", "/invoices"),
        (tr_static(page.session.store.get("lang", "en"), "stock_value"), f"{currency}{d['stock_value']:,.0f}", ft.Icons.INVENTORY, "#0891B2", "/products"),
        (tr_static(page.session.store.get("lang", "en"), "low_stock"), str(d['low_stock']), ft.Icons.ERROR_OUTLINE, "#F59E0B", "/products"),
        (tr_static(page.session.store.get("lang", "en"), "new_customers"), str(d['new_customers']), ft.Icons.PERSON_ADD, "#0D9488", "/customers"),
    ]

    status_bars = ft.Column(spacing=2)
    inv_total = max(d['total_invoices'], 1)
    for label, val, clr in [
        (tr_static(page.session.store.get("lang", "en"), "draft_invoices"), d['draft_inv'], "#94A3B8"),
        (tr_static(page.session.store.get("lang", "en"), "sent_invoices"), d['sent_inv'], "#3B82F6"),
        (tr_static(page.session.store.get("lang", "en"), "partial_invoices"), d['partial_inv'], WARNING),
        (tr_static(page.session.store.get("lang", "en"), "paid_invoices"), d['paid_inv'], SUCCESS),
    ]:
        pct = min(val / inv_total * 100, 100)
        status_bars.controls.append(ft.Column([
            ft.Row([
                ft.Text(label, size=12, color="#475569", expand=True),
                ft.Text(str(val), size=12, weight=ft.FontWeight.BOLD, color="#1E293B"),
            ], spacing=4),
            ft.Stack([
                ft.Container(height=5, bgcolor="#F1F5F9", border_radius=3),
                ft.Container(height=5, width=pct * 2.5, bgcolor=clr, border_radius=3),
            ]),
        ], spacing=3))
        status_bars.controls.append(ft.Container(height=4))

    top_prod_bars = ft.Column(spacing=2)
    max_rev = max((p['revenue'] for p in d['top_products']), default=1)
    for p in d['top_products'][:5]:
        pct = min(p['revenue'] / max_rev * 100, 100)
        top_prod_bars.controls.append(ft.Column([
            ft.Row([
                ft.Text(p['product_name'][:20], size=12, color="#475569", expand=True),
                ft.Text(f"{currency}{p['revenue']:,.0f}", size=12, weight=ft.FontWeight.BOLD, color="#1E293B"),
            ], spacing=4),
            ft.Stack([
                ft.Container(height=5, bgcolor="#F1F5F9", border_radius=3),
                ft.Container(height=5, width=pct * 2.5, bgcolor=PRIMARY, border_radius=3),
            ]),
        ], spacing=3))
        top_prod_bars.controls.append(ft.Container(height=4))

    sales_bars = ft.Column(spacing=2)
    sales_max = max((s['total'] for s in d['sales_trend']), default=1)
    months = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    for s in d['sales_trend'][-6:]:
        m_name = months.get(int(s['m']), s['m'])
        pct = min(s['total'] / sales_max * 100, 100)
        sales_bars.controls.append(ft.Column([
            ft.Row([
                ft.Text(m_name, size=12, color="#475569", width=35),
                ft.Stack([
                    ft.Container(height=5, bgcolor="#F1F5F9", border_radius=3, expand=True),
                    ft.Container(height=5, width=pct * 2.5, bgcolor=SECONDARY, border_radius=3),
                ], expand=True),
                ft.Text(f"{currency}{s['total']:,.0f}", size=11, weight=ft.FontWeight.BOLD, color="#1E293B", width=70, text_align=ft.TextAlign.RIGHT),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=3))
        sales_bars.controls.append(ft.Container(height=4))

    top_selling_col = ft.Column(spacing=2)
    for i, p in enumerate(d['fast_moving'][:3]):
        medals = ["#F59E0B", "#94A3B8", "#CD7F32"]
        top_selling_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(str(i+1), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        width=22, height=22, alignment=ft.alignment.Alignment(0, 0),
                        bgcolor=medals[i], border_radius=6,
                    ),
                    ft.Text(p['product_name'][:25], size=13, color="#475569", expand=True),
                    ft.Text(f"x{p['total_sold']}", size=13, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8, bgcolor="#F8FAFC", border_radius=8,
            )
        )
        top_selling_col.controls.append(ft.Container(height=4))

    top_cust_col = ft.Column(spacing=2)
    for i, c in enumerate(d['top_customers'][:3]):
        top_cust_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(str(i+1), size=11, weight=ft.FontWeight.BOLD, color=SECONDARY),
                        width=22, height=22, alignment=ft.alignment.Alignment(0, 0),
                        border=border_all(1.5, SECONDARY), border_radius=6,
                    ),
                    ft.Text(c['name'][:20], size=13, color="#475569", expand=True),
                    ft.Text(f"{currency}{c['revenue']:,.0f}", size=13, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8, bgcolor="#F8FAFC", border_radius=8,
            )
        )
        top_cust_col.controls.append(ft.Container(height=4))

    page.controls.clear()
    page.bgcolor = "#F1F5F9"
    page.add(ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=20, color=ft.Colors.WHITE),
                                bgcolor="rgba(255,255,255,0.15)", padding=8, border_radius=10,
                            ),
                            ft.Text("mInvoice", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(height=4),
                        ft.Row([
                            ft.Icon(ft.Icons.STORE, size=13, color="rgba(255,255,255,0.7)"),
                            ft.Text(company.name if company else tr_static(page.session.store.get("lang", "en"), "my_company"), size=13, color="rgba(255,255,255,0.85)"),
                        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], expand=True, spacing=0),
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.LOGOUT, size=18, color=ft.Colors.WHITE),
                            padding=8, border_radius=10, ink=True,
                            on_click=logout,
                        ),
                    ], spacing=4),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=14),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(tr_static(page.session.store.get("lang", "en"), "revenue"), size=11, color="rgba(255,255,255,0.6)"),
                            ft.Text(f"{currency}{d['sales_month']:,.0f}", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], spacing=0),
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(tr_static(page.session.store.get("lang", "en"), "outstanding"), size=11, color="rgba(255,255,255,0.6)", text_align=ft.TextAlign.RIGHT),
                            ft.Text(f"{currency}{d['outstanding']:,.0f}", size=22, weight=ft.FontWeight.BOLD, color="#FBBF24"),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ),
                ]),
            ], spacing=0),
            padding=ft.Padding(left=20, top=18, right=16, bottom=20),
            bgcolor=PRIMARY,
            border_radius=ft.BorderRadius(top_left=0, top_right=0, bottom_left=20, bottom_right=20),
            shadow=ft.BoxShadow(blur_radius=20, color="rgba(27,42,74,0.25)", offset=ft.Offset(0, 6)),
        ),
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            length=4,
            expand=True,
            content=ft.Column([
                ft.TabBar(
                    scrollable=True,
                    label_color=PRIMARY,
                    unselected_label_color="#94A3B8",
                    indicator_color=PRIMARY,
                    tabs=[
                        ft.Tab(label=tr_static(page.session.store.get("lang", "en"), "tab_main")),
                        ft.Tab(label=tr_static(page.session.store.get("lang", "en"), "tab_kpi")),
                        ft.Tab(label=tr_static(page.session.store.get("lang", "en"), "tab_signals")),
                        ft.Tab(label=tr_static(page.session.store.get("lang", "en"), "tab_products")),
                    ],
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.Container(height=6),
                                ft.Row([
                                    nav_card(tr_static(page.session.store.get("lang", "en"), "customers"), ft.Icons.PEOPLE, "#059669", "/customers"),
                                    nav_card(tr_static(page.session.store.get("lang", "en"), "products"), ft.Icons.INVENTORY_2, "#0891B2", "/products"),
                                ], spacing=10),
                                ft.Container(height=12),
                                ft.Row([
                                    nav_card(tr_static(page.session.store.get("lang", "en"), "new_quote"), ft.Icons.ADD, "#D97706", "/quotes"),
                                    nav_card(tr_static(page.session.store.get("lang", "en"), "invoices"), ft.Icons.RECEIPT, "#7C3AED", "/invoices"),
                                ], spacing=10),
                                ft.Container(height=8),
                                ft.Row([
                                    nav_card("Bons Livr.", ft.Icons.LOCAL_SHIPPING, "#2563EB", "/delivery_notes"),
                                    nav_card(tr_static(page.session.store.get("lang", "en"), "payments"), ft.Icons.PAYMENTS, "#059669", "/payments"),
                                ], spacing=10),
                            ], spacing=0, scroll=ft.ScrollMode.AUTO),
                            padding=ft.Padding(left=16, right=16, top=0, bottom=16), expand=True,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Container(height=6),
                                ft.Row([
                                    kpi_card(*rows_data[5]),
                                    kpi_card(*rows_data[3]),
                                    kpi_card(*rows_data[4]),
                                ], spacing=8),
                                ft.Container(height=12),
                                ft.Row([
                                    kpi_card(*rows_data[1]),
                                    kpi_card(*rows_data[2]),
                                    kpi_card(*rows_data[0]),
                                ], spacing=8),
                                ft.Container(height=12),
                                section_card(tr_static(page.session.store.get("lang", "en"), "invoices_status"), ft.Icons.RECEIPT, "#7C3AED",
                                    status_bars,
                                ),
                            ], spacing=0, scroll=ft.ScrollMode.AUTO),
                            padding=ft.Padding(left=16, right=16, top=0, bottom=16), expand=True,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Container(height=6),
                                ft.Row([
                                    section_card(tr_static(page.session.store.get("lang", "en"), "stock_signals"), ft.Icons.INVENTORY_2, "#0891B2",
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "low_stock_items"), d['low_stock'], WARNING),
                                        ]),
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "out_of_stock"), d['out_of_stock'], ERROR),
                                        ]),
                                        ft.Container(height=6),
                                        ft.Row([signal_item(tr_static(page.session.store.get("lang", "en"), "below_reorder"), d['below_reorder'], "#F59E0B")]),
                                        ft.Container(height=8),
                                        ft.Text(tr_static(page.session.store.get("lang", "en"), "top_selling"), size=11, weight=ft.FontWeight.BOLD, color="#94A3B8", height=14),
                                        ft.Container(height=4),
                                        top_selling_col,
                                    ),
                                    section_card(tr_static(page.session.store.get("lang", "en"), "customer_signals"), ft.Icons.PEOPLE, "#059669",
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "active_customers"), d['active_customers'], SUCCESS),
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "overdue_customers"), d['overdue_customers'], ERROR),
                                        ], spacing=8),
                                        ft.Container(height=6),
                                        ft.Row([signal_item(tr_static(page.session.store.get("lang", "en"), "total_customers"), d['total_customers'], "#3B82F6")]),
                                        ft.Container(height=8),
                                        ft.Text(tr_static(page.session.store.get("lang", "en"), "top_customers"), size=11, weight=ft.FontWeight.BOLD, color="#94A3B8", height=14),
                                        ft.Container(height=4),
                                        top_cust_col,
                                    ),
                                ], spacing=10),
                                ft.Container(height=8),
                                ft.Row([
                                    section_card(tr_static(page.session.store.get("lang", "en"), "quote_signals"), ft.Icons.DESCRIPTION, "#D97706",
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "draft_quotes"), d['draft_quotes'], "#94A3B8"),
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "validated_quotes"), d['validated_quotes'], SUCCESS),
                                        ], spacing=8),
                                        ft.Container(height=4),
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "sent_quotes"), d['sent_quotes'], "#3B82F6"),
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "confirmed_quotes"), d['confirmed_quotes'], "#7C3AED"),
                                        ], spacing=8),
                                        ft.Container(height=6),
                                        ft.Row([
                                            ft.Column([
                                                ft.Text(tr_static(page.session.store.get("lang", "en"), "quotes_month"), size=10, color="#94A3B8"),
                                                ft.Text(str(d['quotes_month']), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                            ], spacing=1, expand=True),
                                            ft.Column([
                                                ft.Text(tr_static(page.session.store.get("lang", "en"), "amount_month"), size=10, color="#94A3B8", text_align=ft.TextAlign.RIGHT),
                                                ft.Text(f"{currency}{d['quotes_amount_month']:,.0f}", size=14, weight=ft.FontWeight.BOLD, color="#D97706"),
                                            ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END),
                                        ]),
                                    ),
                                    section_card(tr_static(page.session.store.get("lang", "en"), "invoice_signals"), ft.Icons.RECEIPT, "#7C3AED",
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "draft_invoices"), d['draft_inv'], "#94A3B8"),
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "sent_invoices"), d['sent_inv'], "#3B82F6"),
                                        ], spacing=8),
                                        ft.Container(height=4),
                                        ft.Row([
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "partial_invoices"), d['partial_inv'], WARNING),
                                            signal_item(tr_static(page.session.store.get("lang", "en"), "paid_invoices"), d['paid_inv'], SUCCESS),
                                        ], spacing=8),
                                        ft.Container(height=4),
                                        ft.Row([signal_item(tr_static(page.session.store.get("lang", "en"), "overdue_invoices"), d['overdue_count'], ERROR)]),
                                    ),
                                ], spacing=10),
                            ], spacing=0, scroll=ft.ScrollMode.AUTO),
                            padding=ft.Padding(left=16, right=16, top=0, bottom=16), expand=True,
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Container(height=6),
                                ft.Row([
                                    section_card(tr_static(page.session.store.get("lang", "en"), "top_products"), ft.Icons.INVENTORY, PRIMARY,
                                        top_prod_bars,
                                    ),
                                    section_card(tr_static(page.session.store.get("lang", "en"), "sales_trend"), ft.Icons.SHOW_CHART, SECONDARY,
                                        sales_bars,
                                    ),
                                ], spacing=10),
                            ], spacing=0, scroll=ft.ScrollMode.AUTO),
                            padding=ft.Padding(left=16, right=16, top=0, bottom=16), expand=True,
                        ),
                    ],
                ),
            ]),
        ),
    ], expand=True, spacing=0))
    page.update()
