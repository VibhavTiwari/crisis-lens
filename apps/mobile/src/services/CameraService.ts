/**
 * Camera Service
 * 
 * Handles camera permissions, capture, and media upload.
 */
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';

export async function requestCameraPermissions(): Promise<boolean> {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    return status === 'granted';
}

export async function requestMediaLibraryPermissions(): Promise<boolean> {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    return status === 'granted';
}

export async function capturePhoto(): Promise<string | null> {
    try {
        const hasPermission = await requestCameraPermissions();
        if (!hasPermission) {
            throw new Error('Camera permission denied');
        }

        const result = await ImagePicker.launchCameraAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
        });

        if (!result.canceled && result.assets[0]) {
            return result.assets[0].uri;
        }

        return null;
    } catch (error) {
        console.error('Photo capture error:', error);
        return null;
    }
}

export async function pickImageFromLibrary(): Promise<string | null> {
    try {
        const hasPermission = await requestMediaLibraryPermissions();
        if (!hasPermission) {
            throw new Error('Media library permission denied');
        }

        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
        });

        if (!result.canceled && result.assets[0]) {
            return result.assets[0].uri;
        }

        return null;
    } catch (error) {
        console.error('Image picker error:', error);
        return null;
    }
}

export async function compressImage(
    uri: string,
    maxWidth: number = 1200
): Promise<string> {
    try {
        const manipResult = await manipulateAsync(
            uri,
            [{ resize: { width: maxWidth } }],
            { compress: 0.7, format: SaveFormat.JPEG }
        );

        return manipResult.uri;
    } catch (error) {
        console.error('Image compression error:', error);
        return uri; // Return original if compression fails
    }
}

export async function getImageSize(uri: string): Promise<number> {
    try {
        const fileInfo = await FileSystem.getInfoAsync(uri);
        return fileInfo.exists ? fileInfo.size : 0;
    } catch (error) {
        console.error('Get file size error:', error);
        return 0;
    }
}

export function createMediaObject(uri: string): {
    uri: string;
    name: string;
    type: string;
} {
    const filename = uri.split('/').pop() || 'image.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : `image/jpeg`;

    return {
        uri,
        name: filename,
        type,
    };
}
