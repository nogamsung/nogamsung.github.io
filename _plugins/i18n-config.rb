# frozen_string_literal: true

# 언어별 사이트 설정 덮어쓰기 (jekyll-polyglot 보조)
#
# polyglot 은 언어마다 사이트를 따로 빌드하면서 site.active_lang 만 바꿔 준다.
# tagline·description·giscus 언어처럼 _config.yml 의 값 자체가 언어마다 달라야 하는 것은
# `i18n.<lang>` 아래에 적어 두고, 빌드 시작 시점(after_reset)에 site.config 에 깊게 병합한다.
# 기본 언어 빌드에서는 원래 값을 그대로 쓴다.
module NogamsungI18n
  def self.deep_merge(base, over)
    base.merge(over) do |_key, a, b|
      a.is_a?(Hash) && b.is_a?(Hash) ? deep_merge(a, b) : b
    end
  end
end

Jekyll::Hooks.register :site, :after_reset do |site|
  config = site.config
  config['i18n_original'] ||= Marshal.load(Marshal.dump(config.reject { |k, _| k == 'i18n' }))
  lang = config['active_lang'] || config['default_lang']
  overrides = (config['i18n'] || {})[lang]
  next unless overrides.is_a?(Hash)

  NogamsungI18n.deep_merge(config['i18n_original'], overrides).each { |k, v| config[k] = v }
end

# polyglot 은 원문과 번역을 permalink 로 짝짓는다. 그런데 _config.yml defaults 의 permalink 는
# '/posts/:title/' 같은 패턴 그대로라 모든 글이 같은 값이 되어 짝짓기·hreflang·canonical 이 깨진다.
# polyglot 의 coordinate(:post_read, normal) 보다 먼저 패턴을 실제 주소로 풀어 둔다.
Jekyll::Hooks.register :site, :post_read, priority: :high do |site|
  docs = site.collections.values.flat_map(&:docs) + site.pages
  docs.each do |doc|
    permalink = doc.data['permalink'].to_s
    next unless permalink.include?(':')

    doc.data['permalink'] = doc.url
  end
end
