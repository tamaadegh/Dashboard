import importlib
import json
import os
import zipfile
import shutil
import subprocess
import logging

from django.conf import settings
import tempfile

from django.forms import ValidationError
import requests
from nxtbn.core.admin_permissions import IsStoreAdmin
from nxtbn.plugins.utils import PluginHandler
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser
from rest_framework.parsers import JSONParser

from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet



from nxtbn.plugins import PluginType
from nxtbn.plugins.api.dashboard.serializers import  PluginSerializer, PluginUpdateSerializer, ZipFileUploadSerializer
from nxtbn.plugins.manager import PluginPathManager
from nxtbn.plugins.models import Plugin
from nxtbn.users import UserRole



class PluginListView(APIView):
    permission_classes = (IsStoreAdmin,)
    serializer_class = PluginSerializer
    HTTP_PERMISSIONS = {
        UserRole.STORE_MANAGER: {"get"},
        UserRole.ADMIN: {"get"},
        UserRole.ORDER_PROCESSOR: {"get"},
        UserRole.ACCOUNTANT: {"get"},
    }

    def get(self, request):
        # Resolve the plugin directory based on settings.BASE_DIR
        PLUGIN_BASE_DIR = 'nxtbn.plugins.sources'
        plugin_dir = os.path.join(settings.BASE_DIR, *PLUGIN_BASE_DIR.split('.'))

        try:
            # Ensure the directory exists
            if not os.path.exists(plugin_dir):
                return Response({"error": f"Plugin directory '{plugin_dir}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # List directories inside the 'sources' folder
            directories = [d for d in os.listdir(plugin_dir) if os.path.isdir(os.path.join(plugin_dir, d))]
            print(f"Directories found: {directories}")

            plugin_data = []
            for directory in directories:
                meta_file_path = os.path.join(plugin_dir, directory, 'meta.json')
                if os.path.exists(meta_file_path):
                    try:
                        with open(meta_file_path, 'r') as meta_file:
                            plugin_data.append(
                                json.load(meta_file)
                            )
                    except Exception as e:
                        return Response({"error": f"Error reading meta file in '{directory}': {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(plugin_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)