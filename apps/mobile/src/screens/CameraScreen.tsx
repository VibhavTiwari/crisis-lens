import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert } from 'react-native';
import { Camera, Image as ImageIcon, Upload } from 'lucide-react-native';
import { capturePhoto, pickImageFromLibrary, compressImage, createMediaObject } from '../services/CameraService';
import { getCurrentLocation } from '../services/LocationService';
import { api } from '../services/api';

export default function CameraScreen({ navigation }: any) {
    const [capturedImage, setCapturedImage] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);

    const handleCapturePhoto = async () => {
        const uri = await capturePhoto();
        if (uri) {
            setCapturedImage(uri);
        }
    };

    const handlePickImage = async () => {
        const uri = await pickImageFromLibrary();
        if (uri) {
            setCapturedImage(uri);
        }
    };

    const handleUpload = async () => {
        if (!capturedImage) return;

        setIsUploading(true);
        try {
            // Compress image
            const compressedUri = await compressImage(capturedImage);

            // Get location
            const location = await getCurrentLocation();

            // Create media object
            const mediaObject = createMediaObject(compressedUri);

            // Upload to API
            await api.uploadMedia(mediaObject);

            Alert.alert('Success', 'Evidence uploaded successfully');
            setCapturedImage(null);
            navigation.goBack();
        } catch (error) {
            Alert.alert('Error', 'Failed to upload evidence');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <View style={styles.container}>
            {capturedImage ? (
                <View style={styles.preview}>
                    <Image source={{ uri: capturedImage }} style={styles.image} />
                    <View style={styles.actions}>
                        <TouchableOpacity
                            style={[styles.button, styles.retakeButton]}
                            onPress={() => setCapturedImage(null)}
                        >
                            <Text style={styles.buttonText}>Retake</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[styles.button, styles.uploadButton]}
                            onPress={handleUpload}
                            disabled={isUploading}
                        >
                            <Upload size={20} color="#fff" />
                            <Text style={styles.buttonText}>
                                {isUploading ? 'Uploading...' : 'Upload Evidence'}
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>
            ) : (
                <View style={styles.options}>
                    <Text style={styles.title}>Capture Crisis Evidence</Text>

                    <TouchableOpacity style={styles.optionButton} onPress={handleCapturePhoto}>
                        <Camera size={48} color="#3b82f6" />
                        <Text style={styles.optionText}>Take Photo</Text>
                    </TouchableOpacity>

                    <TouchableOpacity style={styles.optionButton} onPress={handlePickImage}>
                        <ImageIcon size={48} color="#3b82f6" />
                        <Text style={styles.optionText}>Choose from Library</Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#000' },
    preview: { flex: 1 },
    image: { flex: 1, resizeMode: 'contain' },
    actions: { position: 'absolute', bottom: 40, left: 0, right: 0, flexDirection: 'row', justifyContent: 'center', gap: 16, paddingHorizontal: 20 },
    button: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, borderRadius: 8, gap: 8 },
    retakeButton: { backgroundColor: '#6b7280' },
    uploadButton: { backgroundColor: '#3b82f6' },
    buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
    options: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', padding: 32 },
    title: { fontSize: 24, fontWeight: 'bold', marginBottom: 48, color: '#1f2937' },
    optionButton: { alignItems: 'center', padding: 32, backgroundColor: '#f9fafb', borderRadius: 16, marginBottom: 24, width: '100%' },
    optionText: { marginTop: 16, fontSize: 18, fontWeight: '600', color: '#374151' },
});
