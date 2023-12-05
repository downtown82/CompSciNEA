class MergeSort:
    def __init__(self):
        self.arr = []
    def sort(self, arr, sort_index):
        self.arr = arr
        self._merge_sort(0, len(arr) - 1, sort_index)
        return self.arr
    def _merge_sort(self, left, right, sort_index):
        if left < right:
            mid = (left + right) // 2
            self._merge_sort(left, mid, sort_index)
            self._merge_sort(mid + 1, right, sort_index)
            self._merge(left, mid, right, sort_index)
    def _merge(self, left, mid, right, sort_index):
        left_arr = self.arr[left:mid + 1]
        right_arr = self.arr[mid + 1:right + 1]
        i = j = 0
        k = left
        while i < len(left_arr) and j < len(right_arr):
            if left_arr[i][sort_index] >= right_arr[j][sort_index]:
                self.arr[k] = left_arr[i]
                i += 1
            else:
                self.arr[k] = right_arr[j]
                j += 1
            k += 1
        while i < len(left_arr):
            self.arr[k] = left_arr[i]
            i += 1
            k += 1
        while j < len(right_arr):
            self.arr[k] = right_arr[j]
            j += 1
            k += 1

class OppositeMergeSort:
    def __init__(self):
        self.arr = []
    def sort(self, arr, sort_index):
        self.arr = arr
        self._merge_sort(0, len(arr) - 1, sort_index)
        return self.arr
    def _merge_sort(self, left, right, sort_index):
        if left < right:
            mid = (left + right) // 2
            self._merge_sort(left, mid, sort_index)
            self._merge_sort(mid + 1, right, sort_index)
            self._merge(left, mid, right, sort_index)
    def _merge(self, left, mid, right, sort_index):
        left_arr = self.arr[left:mid + 1]
        right_arr = self.arr[mid + 1:right + 1]
        i = j = 0
        k = left
        while i < len(left_arr) and j < len(right_arr):
            if left_arr[i][sort_index] <= right_arr[j][sort_index]:
                self.arr[k] = left_arr[i]
                i += 1
            else:
                self.arr[k] = right_arr[j]
                j += 1
            k += 1
        while i < len(left_arr):
            self.arr[k] = left_arr[i]
            i += 1
            k += 1
        while j < len(right_arr):
            self.arr[k] = right_arr[j]
            j += 1
            k += 1