# src/gui/routes.py
@app.route('/')
def provider_list():
    # 伪逻辑：从 ProviderService 获取配置列表
    providers = provider_service.get_all()
    return render_template('providers.html', providers=providers)

@app.route('/add', methods=['POST'])
def add_provider():
    # 伪逻辑：获取表单数据并创建配置
    port = port_manager.allocate_port()
    config = ProviderConfig(name=request.form['name'], ...)
    provider_service.add_provider(config)
    ProcessManager.start_provider(config)
    return redirect('/')