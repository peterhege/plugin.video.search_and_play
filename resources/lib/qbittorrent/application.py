# -*- coding: utf-8 -*-
import json

from .base import Qbittorrent


class Application(Qbittorrent):
    BASE_PATH = 'app'
    URLS = {
        'version': '/version',
        'webapiVersion': '/webapiVersion',
        'buildInfo': '/buildInfo',
        'shutdown': '/shutdown',
        'preferences': '/preferences',
        'setPreferences': '/setPreferences',
        'defaultSavePath': '/defaultSavePath'
    }

    def version(self):  # type: () -> str
        """
        Get application version

        Returns:
            The response is a string with the application version, e.g. v4.1.3
        """
        path = self._get_path('version')
        return self._GET(path, None, {})

    def webapi_version(self):  # type: () -> str
        """
        Get API version

        Returns:
            The response is a string with the WebAPI version, e.g. 2.0
        """
        path = self._get_path('webapiVersion')
        return self._GET(path, None, {})

    def build_info(self):  # type: () -> BuildInfo
        """
        Get build info
        """
        path = self._get_path('buildInfo')
        return BuildInfo(**self._GET(path, None))

    def preferences(self, preferences=None):  # type: (Preferences) -> Preferences
        if not preferences:
            return self.get_preferences()
        return self.set_preferences(preferences)

    def get_preferences(self):  # type: () -> Preferences
        """
        Get application preferences

        Returns:
            The response is a JSON object with several fields (key-value) pairs representing the application's settings.
            The contents may vary depending on which settings are present in qBittorrent.ini.
        """
        path = self._get_path('preferences')
        return Preferences(**self._GET(path, None))

    def set_preferences(self, preferences):  # type: (Preferences) -> Preferences
        """
        Set application preferences
        """
        path = self._get_path('setPreferences')
        kwargs = {k: v for k, v in preferences.__dict__.items() if v is not None}
        params = {'json': json.dumps(kwargs)}
        self._GET(path, params)
        return self.get_preferences()

    def default_save_path(self):  # type: () -> str
        """
        Get default save path

        Returns:
            The response is a string with the default save path, e.g. C:/Users/Dayman/Downloads.
        """
        path = self._get_path('defaultSavePath')
        return self._GET(path, None, {})


class BuildInfo(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-build-info

    Parameters:
        qt (str): QT version
        libtorrent (str): libtorrent version
        boost (str): Boost version
        openssl (str): OpenSSL version
        bitness (int): Application bitness (e.g. 64-bit)
    """
    qt = None  # type: str
    libtorrent = None  # type: str
    boost = None  # type: str
    openssl = None  # type: str
    bitness = None  # type: int

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Preferences(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-application-preferences

    Parameters:
        locale (str): Currently selected language (e.g. en_GB for English)
        create_subfolder_enabled (bool): True if a subfolder should be created when adding a torrent
        start_paused_enabled (bool): True if torrents should be added in a Paused state
        auto_delete_mode (int): TODO
        preallocate_all (bool): True if disk space should be pre-allocated for all files
        incomplete_files_ext (bool): True if ".!qB" should be appended to incomplete files
        auto_tmm_enabled (bool): True if Automatic Torrent Management is enabled by default
        torrent_changed_tmm_enabled (bool): True if torrent should be relocated when its Category changes
        save_path_changed_tmm_enabled (bool): True if torrent should be relocated when the default save path changes
        category_changed_tmm_enabled (bool): True if torrent should be relocated when its Category's save path changes
        save_path (str): Default save path for torrents, separated by slashes
        temp_path_enabled (bool): True if folder for incomplete torrents is enabled
        temp_path (str): Path for incomplete torrents, separated by slashes
        scan_dirs (object): Property: directory to watch for torrent files, value: where torrents loaded from this directory should be downloaded to (see list of possible values below). Slashes are used as path separators; multiple key/value pairs can be specified
        export_dir (str): Path to directory to copy .torrent files to. Slashes are used as path separators
        export_dir_fin (str): Path to directory to copy .torrent files of completed downloads to. Slashes are used as path separators
        mail_notification_enabled (bool): True if e-mail notification should be enabled
        mail_notification_sender (str): e-mail where notifications should originate from
        mail_notification_email (str): e-mail to send notifications to
        mail_notification_smtp (str): smtp server for e-mail notifications
        mail_notification_ssl_enabled (bool): True if smtp server requires SSL connection
        mail_notification_auth_enabled (bool): True if smtp server requires authentication
        mail_notification_username (str): Username for smtp authentication
        mail_notification_password (str): Password for smtp authentication
        autorun_enabled (bool): True if external program should be run after torrent has finished downloading
        autorun_program (str): Program path/name/arguments to run if autorun_enabled is enabled; path is separated by slashes; you can use %f and %n arguments, which will be expanded by qBittorent as path_to_torrent_file and torrent_name (from the GUI; not the .torrent file name) respectively
        queueing_enabled (bool): True if torrent queuing is enabled
        max_active_downloads (int): Maximum number of active simultaneous downloads
        max_active_torrents (int): Maximum number of active simultaneous downloads and uploads
        max_active_uploads (int): Maximum number of active simultaneous uploads
        dont_count_slow_torrents (bool): If true torrents w/o any activity (stalled ones) will not be counted towards max_active_* limits; see dont_count_slow_torrents for more information
        slow_torrent_dl_rate_threshold (int): Download rate in KiB/s for a torrent to be considered "slow"
        slow_torrent_ul_rate_threshold (int): Upload rate in KiB/s for a torrent to be considered "slow"
        slow_torrent_inactive_timer (int): Seconds a torrent should be inactive before considered "slow"
        max_ratio_enabled (bool): True if share ratio limit is enabled
        max_ratio (float): Get the global share ratio limit
        max_ratio_act (int): Action performed when a torrent reaches the maximum share ratio. See list of possible values here below.
        listen_port (int): Port for incoming connections
        upnp (bool): True if UPnP/NAT-PMP is enabled
        random_port (bool): True if the port is randomly selected
        dl_limit (int): Global download speed limit in KiB/s; -1 means no limit is applied
        up_limit (int): Global upload speed limit in KiB/s; -1 means no limit is applied
        max_connec (int): Maximum global number of simultaneous connections
        max_connec_per_torrent (int): Maximum number of simultaneous connections per torrent
        max_uploads (int): Maximum number of upload slots
        max_uploads_per_torrent (int): Maximum number of upload slots per torrent
        stop_tracker_timeout (int): Timeout in seconds for a stopped announce request to trackers
        enable_piece_extent_affinity (bool): True if the advanced libtorrent option piece_extent_affinity is enabled
        bittorrent_protocol (int): Bittorrent Protocol to use (see list of possible values below)
        limit_utp_rate (bool): True if [du]l_limit should be applied to uTP connections; this option is only available in qBittorent built against libtorrent version 0.16.X and higher
        limit_tcp_overhead (bool): True if [du]l_limit should be applied to estimated TCP overhead (service data: e.g. packet headers)
        limit_lan_peers (bool): True if [du]l_limit should be applied to peers on the LAN
        alt_dl_limit (int): Alternative global download speed limit in KiB/s
        alt_up_limit (int): Alternative global upload speed limit in KiB/s
        scheduler_enabled (bool): True if alternative limits should be applied according to schedule
        schedule_from_hour (int): Scheduler starting hour
        schedule_from_min (int): Scheduler starting minute
        schedule_to_hour (int): Scheduler ending hour
        schedule_to_min (int): Scheduler ending minute
        scheduler_days (int): Scheduler days. See possible values here below
        dht (bool): True if DHT is enabled
        pex (bool): True if PeX is enabled
        lsd (bool): True if LSD is enabled
        encryption (int): See list of possible values here below
        anonymous_mode (bool): If true anonymous mode will be enabled; read more here; this option is only available in qBittorent built against libtorrent version 0.16.X and higher
        proxy_type (int): See list of possible values here below
        proxy_ip (str): Proxy IP address or domain name
        proxy_port (int): Proxy port
        proxy_peer_connections (bool): True if peer and web seed connections should be proxified; this option will have any effect only in qBittorent built against libtorrent version 0.16.X and higher
        proxy_auth_enabled (bool): True proxy requires authentication; doesn't apply to SOCKS4 proxies
        proxy_username (str): Username for proxy authentication
        proxy_password (str): Password for proxy authentication
        proxy_torrents_only (bool): True if proxy is only used for torrents
        ip_filter_enabled (bool): True if external IP filter should be enabled
        ip_filter_path (str): Path to IP filter file (.dat, .p2p, .p2b files are supported); path is separated by slashes
        ip_filter_trackers (bool): True if IP filters are applied to trackers
        web_ui_domain_list (str): Comma-separated list of domains to accept when performing Host header validation
        web_ui_address (str): IP address to use for the WebUI
        web_ui_port (int): WebUI port
        web_ui_upnp (bool): True if UPnP is used for the WebUI port
        web_ui_username (str): WebUI username
        web_ui_password (str): For API ≥ v2.3.0: Plaintext WebUI password, not readable, write-only. For API < v2.3.0: MD5 hash of WebUI password, hash is generated from the following string: username:Web UI Access:plain_text_web_ui_password
        web_ui_csrf_protection_enabled (bool): True if WebUI CSRF protection is enabled
        web_ui_clickjacking_protection_enabled (bool): True if WebUI clickjacking protection is enabled
        web_ui_secure_cookie_enabled (bool): True if WebUI cookie Secure flag is enabled
        web_ui_max_auth_fail_count (int): Maximum number of authentication failures before WebUI access ban
        web_ui_ban_duration (int): WebUI access ban duration in seconds
        web_ui_session_timeout (int): Seconds until WebUI is automatically signed off
        web_ui_host_header_validation_enabled (bool): True if WebUI host header validation is enabled
        bypass_local_auth (bool): True if authentication challenge for loopback address (127.0.0.1) should be disabled
        bypass_auth_subnet_whitelist_enabled (bool): True if webui authentication should be bypassed for clients whose ip resides within (at least) one of the subnets on the whitelist
        bypass_auth_subnet_whitelist (str): (White)list of ipv4/ipv6 subnets for which webui authentication should be bypassed; list entries are separated by commas
        alternative_webui_enabled (bool): True if an alternative WebUI should be used
        alternative_webui_path (str): File path to the alternative WebUI
        use_https (bool): True if WebUI HTTPS access is enabled
        ssl_key (str): For API < v2.0.1: SSL keyfile contents (this is a not a path)
        ssl_cert (str): For API < v2.0.1: SSL certificate contents (this is a not a path)
        web_ui_https_key_path (str): For API ≥ v2.0.1: Path to SSL keyfile
        web_ui_https_cert_path (str): For API ≥ v2.0.1: Path to SSL certificate
        dyndns_enabled (bool): True if server DNS should be updated dynamically
        dyndns_service (int): See list of possible values here below
        dyndns_username (str): Username for DDNS service
        dyndns_password (str): Password for DDNS service
        dyndns_domain (str): Your DDNS domain name
        rss_refresh_interval (int): RSS refresh interval
        rss_max_articles_per_feed (int): Max stored articles per RSS feed
        rss_processing_enabled (bool): Enable processing of RSS feeds
        rss_auto_downloading_enabled (bool): Enable auto-downloading of torrents from the RSS feeds
        rss_download_repack_proper_episodes (bool): For API ≥ v2.5.1: Enable downloading of repack/proper Episodes
        rss_smart_episode_filters (str): For API ≥ v2.5.1: List of RSS Smart Episode Filters
        add_trackers_enabled (bool): Enable automatic adding of trackers to new torrents
        add_trackers (str): List of trackers to add to new torrent
        web_ui_use_custom_http_headers_enabled (bool): For API ≥ v2.5.1: Enable custom http headers
        web_ui_custom_http_headers (str): For API ≥ v2.5.1: List of custom http headers
        max_seeding_time_enabled (bool): True enables max seeding time
        max_seeding_time (int): Number of minutes to seed a torrent
        announce_ip (str): TODO
        announce_to_all_tiers (bool): True always announce to all tiers
        announce_to_all_trackers (bool): True always announce to all trackers in a tier
        async_io_threads (int): Number of asynchronous I/O threads
        banned_IPs (str): List of banned IPs
        checking_memory_use (int): Outstanding memory when checking torrents in MiB
        current_interface_address (str): IP Address to bind to. Empty String means All addresses
        current_network_interface (str): Network Interface used
        disk_cache (int): Disk cache used in MiB
        disk_cache_ttl (int): Disk cache expiry interval in seconds
        embedded_tracker_port (int): Port used for embedded tracker
        enable_coalesce_read_write (bool): True enables coalesce reads & writes
        enable_embedded_tracker (bool): True enables embedded tracker
        enable_multi_connections_from_same_ip (bool): True allows multiple connections from the same IP address
        enable_os_cache (bool): True enables os cache
        enable_upload_suggestions (bool): True enables sending of upload piece suggestions
        file_pool_size (int): File pool size
        outgoing_ports_max (int): Maximal outgoing port (0: Disabled)
        outgoing_ports_min (int): Minimal outgoing port (0: Disabled)
        recheck_completed_torrents (bool): True rechecks torrents on completion
        resolve_peer_countries (bool): True resolves peer countries
        save_resume_data_interval (int): Save resume data interval in min
        send_buffer_low_watermark (int): Send buffer low watermark in KiB
        send_buffer_watermark (int): Send buffer watermark in KiB
        send_buffer_watermark_factor (int): Send buffer watermark factor in percent
        socket_backlog_size (int): Socket backlog size
        upload_choking_algorithm (int): Upload choking algorithm used (see list of possible values below)
        upload_slots_behavior (int): Upload slots behavior used (see list of possible values below)
        upnp_lease_duration (int): UPnP lease duration (0: Permanent lease)
        utp_tcp_mixed_mode (int): μTP-TCP mixed mode algorithm (see list of possible values below)
    """
    locale = None  # type: str
    create_subfolder_enabled = None  # type: bool
    start_paused_enabled = None  # type: bool
    auto_delete_mode = None  # type: int
    preallocate_all = None  # type: bool
    incomplete_files_ext = None  # type: bool
    auto_tmm_enabled = None  # type: bool
    torrent_changed_tmm_enabled = None  # type: bool
    save_path_changed_tmm_enabled = None  # type: bool
    category_changed_tmm_enabled = None  # type: bool
    save_path = None  # type: str
    temp_path_enabled = None  # type: bool
    temp_path = None  # type: str
    scan_dirs = None  # type: object
    export_dir = None  # type: str
    export_dir_fin = None  # type: str
    mail_notification_enabled = None  # type: bool
    mail_notification_sender = None  # type: str
    mail_notification_email = None  # type: str
    mail_notification_smtp = None  # type: str
    mail_notification_ssl_enabled = None  # type: bool
    mail_notification_auth_enabled = None  # type: bool
    mail_notification_username = None  # type: str
    mail_notification_password = None  # type: str
    autorun_enabled = None  # type: bool
    autorun_program = None  # type: str
    queueing_enabled = None  # type: bool
    max_active_downloads = None  # type: int
    max_active_torrents = None  # type: int
    max_active_uploads = None  # type: int
    dont_count_slow_torrents = None  # type: bool
    slow_torrent_dl_rate_threshold = None  # type: int
    slow_torrent_ul_rate_threshold = None  # type: int
    slow_torrent_inactive_timer = None  # type: int
    max_ratio_enabled = None  # type: bool
    max_ratio = None  # type: float
    max_ratio_act = None  # type: int
    listen_port = None  # type: int
    upnp = None  # type: bool
    random_port = None  # type: bool
    dl_limit = None  # type: int
    up_limit = None  # type: int
    max_connec = None  # type: int
    max_connec_per_torrent = None  # type: int
    max_uploads = None  # type: int
    max_uploads_per_torrent = None  # type: int
    stop_tracker_timeout = None  # type: int
    enable_piece_extent_affinity = None  # type: bool
    bittorrent_protocol = None  # type: int
    limit_utp_rate = None  # type: bool
    limit_tcp_overhead = None  # type: bool
    limit_lan_peers = None  # type: bool
    alt_dl_limit = None  # type: int
    alt_up_limit = None  # type: int
    scheduler_enabled = None  # type: bool
    schedule_from_hour = None  # type: int
    schedule_from_min = None  # type: int
    schedule_to_hour = None  # type: int
    schedule_to_min = None  # type: int
    scheduler_days = None  # type: int
    dht = None  # type: bool
    pex = None  # type: bool
    lsd = None  # type: bool
    encryption = None  # type: int
    anonymous_mode = None  # type: bool
    proxy_type = None  # type: int
    proxy_ip = None  # type: str
    proxy_port = None  # type: int
    proxy_peer_connections = None  # type: bool
    proxy_auth_enabled = None  # type: bool
    proxy_username = None  # type: str
    proxy_password = None  # type: str
    proxy_torrents_only = None  # type: bool
    ip_filter_enabled = None  # type: bool
    ip_filter_path = None  # type: str
    ip_filter_trackers = None  # type: bool
    web_ui_domain_list = None  # type: str
    web_ui_address = None  # type: str
    web_ui_port = None  # type: int
    web_ui_upnp = None  # type: bool
    web_ui_username = None  # type: str
    web_ui_password = None  # type: str
    web_ui_csrf_protection_enabled = None  # type: bool
    web_ui_clickjacking_protection_enabled = None  # type: bool
    web_ui_secure_cookie_enabled = None  # type: bool
    web_ui_max_auth_fail_count = None  # type: int
    web_ui_ban_duration = None  # type: int
    web_ui_session_timeout = None  # type: int
    web_ui_host_header_validation_enabled = None  # type: bool
    bypass_local_auth = None  # type: bool
    bypass_auth_subnet_whitelist_enabled = None  # type: bool
    bypass_auth_subnet_whitelist = None  # type: str
    alternative_webui_enabled = None  # type: bool
    alternative_webui_path = None  # type: str
    use_https = None  # type: bool
    ssl_key = None  # type: str
    ssl_cert = None  # type: str
    web_ui_https_key_path = None  # type: str
    web_ui_https_cert_path = None  # type: str
    dyndns_enabled = None  # type: bool
    dyndns_service = None  # type: int
    dyndns_username = None  # type: str
    dyndns_password = None  # type: str
    dyndns_domain = None  # type: str
    rss_refresh_interval = None  # type: int
    rss_max_articles_per_feed = None  # type: int
    rss_processing_enabled = None  # type: bool
    rss_auto_downloading_enabled = None  # type: bool
    rss_download_repack_proper_episodes = None  # type: bool
    rss_smart_episode_filters = None  # type: str
    add_trackers_enabled = None  # type: bool
    add_trackers = None  # type: str
    web_ui_use_custom_http_headers_enabled = None  # type: bool
    web_ui_custom_http_headers = None  # type: str
    max_seeding_time_enabled = None  # type: bool
    max_seeding_time = None  # type: int
    announce_ip = None  # type: str
    announce_to_all_tiers = None  # type: bool
    announce_to_all_trackers = None  # type: bool
    async_io_threads = None  # type: int
    banned_IPs = None  # type: str
    checking_memory_use = None  # type: int
    current_interface_address = None  # type: str
    current_network_interface = None  # type: str
    disk_cache = None  # type: int
    disk_cache_ttl = None  # type: int
    embedded_tracker_port = None  # type: int
    enable_coalesce_read_write = None  # type: bool
    enable_embedded_tracker = None  # type: bool
    enable_multi_connections_from_same_ip = None  # type: bool
    enable_os_cache = None  # type: bool
    enable_upload_suggestions = None  # type: bool
    file_pool_size = None  # type: int
    outgoing_ports_max = None  # type: int
    outgoing_ports_min = None  # type: int
    recheck_completed_torrents = None  # type: bool
    resolve_peer_countries = None  # type: bool
    save_resume_data_interval = None  # type: int
    send_buffer_low_watermark = None  # type: int
    send_buffer_watermark = None  # type: int
    send_buffer_watermark_factor = None  # type: int
    socket_backlog_size = None  # type: int
    upload_choking_algorithm = None  # type: int
    upload_slots_behavior = None  # type: int
    upnp_lease_duration = None  # type: int
    utp_tcp_mixed_mode = None  # type: int
    max_concurrent_http_announces = None  # type: int
    block_peers_on_privileged_ports = None  # type: bool
    peer_tos = None  # type: int
    ssrf_mitigation = None  # type: bool
    torrent_content_layout = None  # type: str
    peer_turnover_interval = None  # type: int
    validate_https_tracker_certificate = None  # type: bool
    peer_turnover_cutoff = None  # type: int
    peer_turnover = None  # type: int
    hashing_threads = None  # type: int
    idn_support_enabled = None  # type: bool

    def __init__(
            self,
            locale=None,  # type: str
            create_subfolder_enabled=None,  # type: bool
            start_paused_enabled=None,  # type: bool
            auto_delete_mode=None,  # type: int
            preallocate_all=None,  # type: bool
            incomplete_files_ext=None,  # type: bool
            auto_tmm_enabled=None,  # type: bool
            torrent_changed_tmm_enabled=None,  # type: bool
            save_path_changed_tmm_enabled=None,  # type: bool
            category_changed_tmm_enabled=None,  # type: bool
            save_path=None,  # type: str
            temp_path_enabled=None,  # type: bool
            temp_path=None,  # type: str
            scan_dirs=None,  # type: object
            export_dir=None,  # type: str
            export_dir_fin=None,  # type: str
            mail_notification_enabled=None,  # type: bool
            mail_notification_sender=None,  # type: str
            mail_notification_email=None,  # type: str
            mail_notification_smtp=None,  # type: str
            mail_notification_ssl_enabled=None,  # type: bool
            mail_notification_auth_enabled=None,  # type: bool
            mail_notification_username=None,  # type: str
            mail_notification_password=None,  # type: str
            autorun_enabled=None,  # type: bool
            autorun_program=None,  # type: str
            queueing_enabled=None,  # type: bool
            max_active_downloads=None,  # type: int
            max_active_torrents=None,  # type: int
            max_active_uploads=None,  # type: int
            dont_count_slow_torrents=None,  # type: bool
            slow_torrent_dl_rate_threshold=None,  # type: int
            slow_torrent_ul_rate_threshold=None,  # type: int
            slow_torrent_inactive_timer=None,  # type: int
            max_ratio_enabled=None,  # type: bool
            max_ratio=None,  # type: float
            max_ratio_act=None,  # type: int
            listen_port=None,  # type: int
            upnp=None,  # type: bool
            random_port=None,  # type: bool
            dl_limit=None,  # type: int
            up_limit=None,  # type: int
            max_connec=None,  # type: int
            max_connec_per_torrent=None,  # type: int
            max_uploads=None,  # type: int
            max_uploads_per_torrent=None,  # type: int
            stop_tracker_timeout=None,  # type: int
            enable_piece_extent_affinity=None,  # type: bool
            bittorrent_protocol=None,  # type: int
            limit_utp_rate=None,  # type: bool
            limit_tcp_overhead=None,  # type: bool
            limit_lan_peers=None,  # type: bool
            alt_dl_limit=None,  # type: int
            alt_up_limit=None,  # type: int
            scheduler_enabled=None,  # type: bool
            schedule_from_hour=None,  # type: int
            schedule_from_min=None,  # type: int
            schedule_to_hour=None,  # type: int
            schedule_to_min=None,  # type: int
            scheduler_days=None,  # type: int
            dht=None,  # type: bool
            pex=None,  # type: bool
            lsd=None,  # type: bool
            encryption=None,  # type: int
            anonymous_mode=None,  # type: bool
            proxy_type=None,  # type: int
            proxy_ip=None,  # type: str
            proxy_port=None,  # type: int
            proxy_peer_connections=None,  # type: bool
            proxy_auth_enabled=None,  # type: bool
            proxy_username=None,  # type: str
            proxy_password=None,  # type: str
            proxy_torrents_only=None,  # type: bool
            ip_filter_enabled=None,  # type: bool
            ip_filter_path=None,  # type: str
            ip_filter_trackers=None,  # type: bool
            web_ui_domain_list=None,  # type: str
            web_ui_address=None,  # type: str
            web_ui_port=None,  # type: int
            web_ui_upnp=None,  # type: bool
            web_ui_username=None,  # type: str
            web_ui_password=None,  # type: str
            web_ui_csrf_protection_enabled=None,  # type: bool
            web_ui_clickjacking_protection_enabled=None,  # type: bool
            web_ui_secure_cookie_enabled=None,  # type: bool
            web_ui_max_auth_fail_count=None,  # type: int
            web_ui_ban_duration=None,  # type: int
            web_ui_session_timeout=None,  # type: int
            web_ui_host_header_validation_enabled=None,  # type: bool
            bypass_local_auth=None,  # type: bool
            bypass_auth_subnet_whitelist_enabled=None,  # type: bool
            bypass_auth_subnet_whitelist=None,  # type: str
            alternative_webui_enabled=None,  # type: bool
            alternative_webui_path=None,  # type: str
            use_https=None,  # type: bool
            ssl_key=None,  # type: str
            ssl_cert=None,  # type: str
            web_ui_https_key_path=None,  # type: str
            web_ui_https_cert_path=None,  # type: str
            dyndns_enabled=None,  # type: bool
            dyndns_service=None,  # type: int
            dyndns_username=None,  # type: str
            dyndns_password=None,  # type: str
            dyndns_domain=None,  # type: str
            rss_refresh_interval=None,  # type: int
            rss_max_articles_per_feed=None,  # type: int
            rss_processing_enabled=None,  # type: bool
            rss_auto_downloading_enabled=None,  # type: bool
            rss_download_repack_proper_episodes=None,  # type: bool
            rss_smart_episode_filters=None,  # type: str
            add_trackers_enabled=None,  # type: bool
            add_trackers=None,  # type: str
            web_ui_use_custom_http_headers_enabled=None,  # type: bool
            web_ui_custom_http_headers=None,  # type: str
            max_seeding_time_enabled=None,  # type: bool
            max_seeding_time=None,  # type: int
            announce_ip=None,  # type: str
            announce_to_all_tiers=None,  # type: bool
            announce_to_all_trackers=None,  # type: bool
            async_io_threads=None,  # type: int
            banned_IPs=None,  # type: str
            checking_memory_use=None,  # type: int
            current_interface_address=None,  # type: str
            current_network_interface=None,  # type: str
            disk_cache=None,  # type: int
            disk_cache_ttl=None,  # type: int
            embedded_tracker_port=None,  # type: int
            enable_coalesce_read_write=None,  # type: bool
            enable_embedded_tracker=None,  # type: bool
            enable_multi_connections_from_same_ip=None,  # type: bool
            enable_os_cache=None,  # type: bool
            enable_upload_suggestions=None,  # type: bool
            file_pool_size=None,  # type: int
            outgoing_ports_max=None,  # type: int
            outgoing_ports_min=None,  # type: int
            recheck_completed_torrents=None,  # type: bool
            resolve_peer_countries=None,  # type: bool
            save_resume_data_interval=None,  # type: int
            send_buffer_low_watermark=None,  # type: int
            send_buffer_watermark=None,  # type: int
            send_buffer_watermark_factor=None,  # type: int
            socket_backlog_size=None,  # type: int
            upload_choking_algorithm=None,  # type: int
            upload_slots_behavior=None,  # type: int
            upnp_lease_duration=None,  # type: int
            utp_tcp_mixed_mode=None,  # type: int
            max_concurrent_http_announces=None,  # type: int
            block_peers_on_privileged_ports=None,  # type: bool
            peer_tos=None,  # type: int
            ssrf_mitigation=None,  # type: bool
            torrent_content_layout=None,  # type: str
            peer_turnover_interval=None,  # type: int
            validate_https_tracker_certificate=None,  # type: bool
            peer_turnover_cutoff=None,  # type: int
            peer_turnover=None,  # type: int
            hashing_threads=None,  # type: int
            idn_support_enabled=None,  # type: bool
            **kwargs
    ):
        for k, v in locals().iteritems():
            if k == 'kwargs':
                for k2, v2 in v.items():
                    setattr(self, k2, v2)
            if k != 'self':
                setattr(self, k, v)
