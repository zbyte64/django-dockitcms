class ManifestFixtures(object):
    def collection_data_fixture(self):
        return {}
    
    def viewpoint_fixture(self):
        return [{
            "pk": "31",
            "natural_key": {
                "url": "/teams/",
                "subsite": "Root",
            },
            "model": "dockitcms.viewpoint",
            "fields": {
                "list_template_html": "",
                "view_type": "dockitcms.listing",
                "url": "/teams/",
                "detail_template_source": "name",
                "mixins": [
                    "widgetblock.widgets"
                ],
                "paginate_by": None,
                "list_template_name": "dockitcms/list.html",
                "detail_template_html": "",
                "detail_template_name": "dockitcms/detail.html",
                "index": {"uuid": "123456789"},
                "list_template_source": "name",
                "widgets": [],
                "slug_field": "",
                "canonical": True,
                "subsite": {"name": "Root"},
                "list_content": "{% for object in object_list %}\r\n<a href=\"{{object.get_absolute_url}}\">{{object}}</a>\r\n{% endfor %}",
                "detail_content": "{% for product in object.products %}\r\n{{product}}\r\n{% endfor %}"
            }
        },
        {
            "pk": "33",
            "model": "dockitcms.viewpoint",
            "natural_key": {
                "url": "/team/",
                "subsite": "Root",
            },
            "fields": {
                "index": {"uuid": "123456789"},
                "view_type": "dockitcms.detailview",
                "url": "/team/",
                "template_name": "dockitcms/detail.html",
                "template_html": "{{ object }} \r\n\r\n{{ object.products }}\r\n",
                "mixins": [],
                "content": "",
                "slug_field": "slug",
                "template_source": "html",
                "subsite": {"name": "Root"},
                "canonical": False
            }
        }]
    
    def application_fixture(self):
        return [{
            "pk": "2",
            "model": "dockitcms.application",
            "natural_key": {
                "slug": "test",
            },
            "fields": {
                "name": "Test",
                "slug": "test",
            }
        }]
    
    def subsite_fixture(self):
        return [{
            "pk": "29",
            "model": "dockitcms.subsite",
            "natural_key": {
                "name": "Root",
            },
            "fields": {
                "widgets": [],
                "url": "/",
                "mixins": [
                    "widgetblock.widgets"
                ],
                "name": "Root",
                "sites": [
                    1
                ]
            }
        }]
    
    def index_fixture(self):
        return [{
            "pk": "27",
            "model": "dockitcms.index",
            "natural_key": {
                "uuid": "123456789"
            },
            "fields": {
                "name": "Team all",
                "parameters": [
                    {
                        "operation": "exact",
                        "key": "slug",
                    }
                ],
                "mixins": [],
                "collection": {"key": "team"},
                "index_type": "dockitcms.filteredcollection",
                "inclusions": [],
                "exclusions": []
            }
        }]
    
    def collection_fixture(self):
        return [{
            "pk": "4",
            "model": "dockitcms.basecollection",
            "natural_key": {
                "key": "team",
            },
            "fields": {
                "inherit_from": "",
                "title": "Team",
                "fields": [
                    {
                        "field_type": "ComplexListField",
                        "name": "members",
                        "object_label": "",
                        "fields": [
                            {
                                "field_type": "ComplexListField",
                                "name": "gallery",
                                "object_label": "",
                                "fields": [
                                    {
                                        "field_type": "CharField",
                                        "name": "name",
                                        "default": "",
                                        "blank": False,
                                        "help_text": "",
                                        "null": False,
                                        "verbose_name": ""
                                    },
                                    {
                                        "field_type": "ImageField",
                                        "name": "image",
                                        "default": "",
                                        "upload_to": "",
                                        "blank": False,
                                        "help_text": "",
                                        "null": False,
                                        "verbose_name": ""
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "field_type": "CharField",
                        "name": "name",
                        "default": "",
                        "blank": False,
                        "help_text": "",
                        "null": False,
                        "verbose_name": ""
                    },
                    {
                        "field_type": "SlugField",
                        "name": "slug",
                        "default": "",
                        "blank": False,
                        "help_text": "",
                        "null": False,
                        "verbose_name": ""
                    }
                ],
                "mixins": [],
                "admin_options": {
                    "list_per_page": 100,
                    "list_display": [],
                },
                "application": {'slug':'test'},
                "collection_type": "document",
                "key": "team",
                "object_label": ""
            }
        }]
