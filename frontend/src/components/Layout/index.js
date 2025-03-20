const menuTheme = {
  components: {
    Menu: {
      itemColor: 'rgba(0, 0, 0, 0.88)',
      itemHoverColor: '#1890ff',
      itemSelectedColor: '#1890ff',
      itemBg: 'transparent',
      itemSelectedBg: '#e6f4ff',
      itemHeight: 40,
      itemBorderRadius: 4,
      itemPaddingInline: 12,
      subMenuItemBg: 'transparent'
    }
  }
};

return (
  <ConfigProvider theme={menuTheme}>
    <Layout style={{ minHeight: '100vh' }}>
      {/* ... rest of the code ... */}
    </Layout>
  </ConfigProvider>
); 