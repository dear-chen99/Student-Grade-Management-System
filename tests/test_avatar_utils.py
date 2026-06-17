"""Avatar 工具模块单元测试.

测试 src/utils/avatar_utils.py 中的头像目录获取、加载头像、更换头像
及内部常量等功能。
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.utils import avatar_utils


class TestGetAvatarDir:
    """测试 get_avatar_dir 函数。"""

    def test_returns_absolute_path(self):
        """返回绝对路径.

        预期结果：路径为绝对路径，且包含 "avatars" 子目录。
        """
        path = avatar_utils.get_avatar_dir()
        assert os.path.isabs(path)
        assert "avatars" in path


class TestLoadAvatar:
    """测试 load_avatar 函数。"""

    def test_empty_path(self):
        """空路径时应清空 label.

        预期结果：label.config 被调用，image 和 text 均设为空。
        """
        label = MagicMock()
        avatar_utils.load_avatar(label, "")
        label.config.assert_called_once_with(text="", image="")

    def test_nonexistent_path(self):
        """路径不存在时应清空 label.

        预期结果：label.config 被调用，image 和 text 均设为空。
        """
        label = MagicMock()
        avatar_utils.load_avatar(label, "nonexistent.png")
        label.config.assert_called_once_with(text="", image="")

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    @patch("src.utils.avatar_utils.Image.open")
    @patch("src.utils.avatar_utils.ImageTk.PhotoImage")
    def test_load_avatar_success(self, mock_photo, mock_open):
        """成功加载头像.

        使用 mock 的 PIL 打开图片并生成 PhotoImage，
        预期 label.config 被调用并传入 image 和空 text。
        """
        label = MagicMock()
        mock_img = MagicMock()
        mock_img.resize.return_value = mock_img
        mock_open.return_value = mock_img
        mock_photo.return_value = MagicMock()

        with patch("os.path.exists", return_value=True):
            avatar_utils.load_avatar(label, "img/avatars/test.png")
            label.config.assert_called_with(image=mock_photo.return_value, text="")

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    def test_load_avatar_exception(self):
        """加载头像异常时应清空 label.

        模拟 Image.open 抛出异常，预期 label 被清空。
        """
        label = MagicMock()
        with patch("os.path.exists", return_value=True):
            with patch(
                "src.utils.avatar_utils.Image.open",
                side_effect=Exception("bad image"),
            ):
                avatar_utils.load_avatar(label, "img/avatars/bad.png")
                label.config.assert_called_with(text="", image="")


class TestChangeAvatar:
    """测试 change_avatar 函数。"""

    def test_pil_not_available(self):
        """PIL 不可用时返回 None.

        预期结果：函数直接返回 None，不执行后续文件操作。
        """
        with patch.object(avatar_utils, "PIL_AVAILABLE", False):
            result = avatar_utils.change_avatar(MagicMock(), "", MagicMock())
            assert result is None

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    @patch("src.utils.avatar_utils.filedialog.askopenfilename")
    @patch("src.utils.avatar_utils.shutil.copy2")
    @patch("src.utils.avatar_utils.os.makedirs")
    def test_change_avatar_success(self, mock_makedirs, mock_copy, mock_ask):
        """成功更换头像.

        模拟用户选择新图片，预期头像文件被复制到 avatars 目录，
        且回调函数被调用一次。
        """
        mock_ask.return_value = "D:/pictures/new.png"
        callback = MagicMock()
        parent = MagicMock()

        with patch("os.path.exists", return_value=False):
            with patch("os.remove"):
                result = avatar_utils.change_avatar(parent, "", callback)
                assert result is not None
                assert result.endswith(".png")
                callback.assert_called_once()

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    @patch(
        "src.utils.avatar_utils.filedialog.askopenfilename",
        return_value="",
    )
    def test_change_avatar_cancelled(self, mock_ask):
        """用户取消选择时返回 None.

        模拟 askopenfilename 返回空字符串，预期函数返回 None。
        """
        result = avatar_utils.change_avatar(MagicMock(), "", MagicMock())
        assert result is None

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    @patch("src.utils.avatar_utils.filedialog.askopenfilename")
    @patch("src.utils.avatar_utils.shutil.copy2")
    @patch("src.utils.avatar_utils.os.makedirs")
    def test_change_avatar_deletes_old(self, mock_makedirs, mock_copy, mock_ask):
        """更换头像时删除旧头像.

        模拟旧头像文件存在，预期 os.remove 被调用一次。
        """
        mock_ask.return_value = "D:/pictures/new.png"
        callback = MagicMock()
        parent = MagicMock()

        with patch("os.path.exists", return_value=True):
            with patch("os.remove") as mock_remove:
                avatar_utils.change_avatar(parent, "img/avatars/old.png", callback)
                mock_remove.assert_called_once()

    @patch.object(avatar_utils, "PIL_AVAILABLE", True)
    @patch("src.utils.avatar_utils.filedialog.askopenfilename")
    @patch("src.utils.avatar_utils.shutil.copy2")
    @patch("src.utils.avatar_utils.os.makedirs")
    def test_change_avatar_exception(self, mock_makedirs, mock_copy, mock_ask):
        """复制文件异常时返回 None.

        模拟 shutil.copy2 抛出异常，预期函数返回 None。
        """
        mock_ask.return_value = "D:/pictures/new.png"
        mock_copy.side_effect = Exception("disk full")
        result = avatar_utils.change_avatar(MagicMock(), "", MagicMock())
        assert result is None


class TestAvatarUtilsInternals:
    """测试 avatar_utils 内部逻辑。"""

    def test_project_root_defined(self):
        """项目根目录已定义.

        预期结果：_PROJECT_ROOT 存在且为绝对路径。
        """
        assert hasattr(avatar_utils, "_PROJECT_ROOT")
        assert os.path.isabs(avatar_utils._PROJECT_ROOT)
